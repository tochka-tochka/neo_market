import pytest
import json
import uuid
import pika
from io import BytesIO
from PIL import Image
from django.urls import reverse
from rest_framework import status
from src.models.product import Category, Product, ProductStatus, SKU
from src.models.user import Seller

@pytest.fixture
def test_category(db):
    return Category.objects.create(
        id="e36e66d9-3c26-4085-a7d7-4be7132a46e5",
        value="Test Category",
        slug="test_category"
    )

@pytest.fixture
def dummy_image():
    file_res = BytesIO()
    image = Image.new('RGB', (100, 100))
    image.save(file_res, 'JPEG')
    file_res.name = 'test.jpg'
    file_res.seek(0)
    return file_res

@pytest.fixture
def base_data(test_category, dummy_image):
    return {
        "title": "test",
        "description": "test",
        "category": str(test_category.id),
        "images": dummy_image,
        "characteristics": json.dumps([{"name": "test", "value": "test"}])
    }

@pytest.fixture
def product_factory(db, test_user, test_category):
    """Фабрика для создания продуктов с разным состоянием"""
    def _make_product(seller=test_user, status=ProductStatus.CREATED, **kwargs):
        return Product.objects.create(
            title=kwargs.pop('title', "Test Product"),
            description="Test Description",
            seller=seller,
            category=test_category,
            status=status,
            **kwargs
        )
    return _make_product

@pytest.fixture
def product(product_factory):
    return product_factory()

@pytest.fixture
def product_with_skus(product_factory):
    p = product_factory(title="Product with SKU")
    SKU.objects.create(product=p, name="sku1", price=100, cost_price=80, active_quantity=10)
    SKU.objects.create(product=p, name="sku2", price=200, cost_price=150, active_quantity=5)
    return p

@pytest.mark.django_db
class TestProductAPI:
    
    def get_rabbitmq_message(self, queue_name, timeout=5):
        """Утилитный метод для получения сообщения"""
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672))
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True, arguments={'x-queue-type': 'quorum'})
        
        received_body = None
        def callback(ch, method, properties, body):
            nonlocal received_body
            received_body = json.loads(body.decode())
            ch.stop_consuming()

        channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        try:
            connection.process_data_events(time_limit=timeout)
        finally:
            connection.close()
        return received_body

    def _clear_queues(self):
        """Вспомогательный метод для очистки очередей перед/после теста"""
        self.get_rabbitmq_message('moder', timeout=0.1)
        self.get_rabbitmq_message('b2c', timeout=0.1)

    def test_create_product_success(self, jwt_client, base_data):
        url = reverse('products')
        response = jwt_client.post(url, base_data, format='multipart')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()['status'] == 'CREATED'

    def test_seller_id_taken_from_jwt(self, jwt_client, test_user, base_data):
        url = reverse('products')
        response = jwt_client.post(url, base_data, format='multipart')
        assert response.json()['seller']['id'] == str(test_user.id)

    @pytest.mark.parametrize("field_to_remove", ["images", "category"])
    def test_missing_fields_returns_400(self, jwt_client, base_data, field_to_remove):
        del base_data[field_to_remove]
        response = jwt_client.post(reverse('products'), base_data, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize("initial_status", [ProductStatus.CREATED, ProductStatus.BLOCKED])
    def test_edit_triggers_moderation_event(self, jwt_client, test_user, product_factory, base_data, initial_status):
        product = product_factory(status=initial_status)
        url = reverse('product-detail', args=[product.id])
        
        self._clear_queues()
        response = jwt_client.patch(url, base_data, format='multipart')

        assert response.status_code == status.HTTP_200_OK
        assert response.json()['status'] == ProductStatus.ON_MODERATION

        msg = self.get_rabbitmq_message('moder')
        assert msg and msg['product_id'] == str(product.id)
        assert 'idempotency_key' in msg

    def test_edit_hard_blocked_returns_403(self, jwt_client, product_factory, base_data):
        product = product_factory(status=ProductStatus.HARD_BLOCKED)
        response = jwt_client.patch(reverse('product-detail', args=[product.id]), base_data, format='multipart')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_edit_others_product_returns_403(self, jwt_client, product_factory, base_data):
        other_seller = Seller.objects.create_user(username="other", password="pass")
        product = product_factory(seller=other_seller)
        response = jwt_client.patch(reverse('product-detail', args=[product.id]), base_data, format='multipart')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_sets_deleted_true(self, jwt_client, product):
        response = jwt_client.delete(reverse('product-detail', args=[product.id]))
        
        self._clear_queues()
        assert response.status_code == status.HTTP_204_NO_CONTENT
        product.refresh_from_db()
        assert product.deleted is True

    def test_delete_emits_event_to_moderation(self, jwt_client, test_user, product):
        jwt_client.delete(reverse('product-detail', args=[product.id]))
        
        msg = self.get_rabbitmq_message('moder')
        self.get_rabbitmq_message('b2c', timeout=0.1)
        
        assert msg and msg['event'] == 'DELETED'
        assert msg['product_id'] == str(product.id)

    def test_delete_emits_product_deleted_to_b2c(self, jwt_client, product_with_skus):
        sku_ids = list(product_with_skus.skus.values_list('id', flat=True))
        jwt_client.delete(reverse('product-detail', args=[product_with_skus.id]))

        self.get_rabbitmq_message('moder', timeout=0.1)
        msg = self.get_rabbitmq_message('b2c')
        
        assert msg and msg['event'] == 'PRODUCT_DELETED'
        assert set(msg['sku_ids']) == set([str(sid) for sid in sku_ids])

    def test_delete_already_deleted_returns_400(self, jwt_client, product):
        product.deleted = True
        product.save()
        response = jwt_client.delete(reverse('product-detail', args=[product.id]))
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_deleted_product_not_in_seller_list(self, jwt_client, test_user, product, product_factory):
        product_factory(title="Active Product")
        
        product.deleted = True
        product.save()
        
        response = jwt_client.get(reverse('my-products'))
        data = response.json()
        
        assert len(data['products']) == 1
        assert str(product.id) not in [p['id'] for p in data['products']]