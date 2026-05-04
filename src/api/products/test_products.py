import pytest
import json
import uuid
import pika
from io import BytesIO
from PIL import Image
from django.urls import reverse
from rest_framework import status
from src.models.product import Category, Product, ProductStatus
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
    """Фабрика для создания тестового изображения"""
    file_res = BytesIO()
    image = Image.new('RGB', (100, 100))
    image.save(file_res, 'JPEG')
    file_res.name = 'test.jpg'
    file_res.seek(0)
    return file_res

@pytest.fixture
def base_data(test_category, dummy_image):
    """Базовая нагрузка для POST/PATCH запросов"""
    return {
        "title": "test",
        "description": "test",
        "category": str(test_category.id),
        "images": dummy_image,
        "characteristics": json.dumps([{"name": "test", "value": "test"}])
    }

@pytest.mark.django_db
class TestProductAPI:
    
    def get_rabbitmq_message(self, queue_name='moder'):
        """Утилитный метод для получения одного сообщения из RabbitMQ"""
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
            connection.process_data_events(time_limit=5)
        finally:
            connection.close()
        return received_body

    def test_create_product_success(self, jwt_client, base_data):
        url = reverse('products')
        response = jwt_client.post(url, base_data, format='multipart')
        
        assert response.status_code == status.HTTP_201_CREATED, response.json()
        assert response.json()['status'] == 'CREATED'
        assert response.json()['skus'] == []

    def test_seller_id_taken_from_jwt(self, jwt_client, test_user, base_data):
        url = reverse('products')
        response = jwt_client.post(url, base_data, format='multipart')
        
        assert response.json()['seller']['id'] == str(test_user.id)

    @pytest.mark.parametrize("field_to_remove", ["images", "category"])
    def test_missing_fields_returns_400(self, jwt_client, base_data, field_to_remove):
        url = reverse('products')
        del base_data[field_to_remove]
        
        response = jwt_client.post(url, base_data, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize("invalid_payload", [
        {"category": "e36e66d9-3c26-4085-a7d7-4be7132a46e6"},
        {"characteristics": json.dumps([{"name": 10, "value": 20}])}
    ])
    def test_invalid_data_returns_400(self, jwt_client, base_data, invalid_payload):
        url = reverse('products')
        base_data.update(invalid_payload)
        
        response = jwt_client.post(url, base_data, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize("initial_status", [
        ProductStatus.CREATED, 
        ProductStatus.BLOCKED
    ])
    def test_edit_triggers_moderation_event(self, jwt_client, test_user, test_category, base_data, initial_status):
        product = Product.objects.create(
            title="Old Title", seller_id=test_user.id, category=test_category, status=initial_status
        )
        url = reverse('specific-product', args=[product.id])
        
        self.get_rabbitmq_message() 

        response = jwt_client.patch(url, base_data, format='multipart')

        assert response.status_code == status.HTTP_200_OK
        assert response.json()['status'] == ProductStatus.ON_MODERATION

        msg = self.get_rabbitmq_message()
        assert msg is not None
        assert msg['product_id'] == str(product.id)
        assert msg['seller_id'] == str(test_user.id)
        assert 'idempotency_key' in msg

    def test_edit_hard_blocked_returns_403(self, jwt_client, test_user, test_category, base_data):
        product = Product.objects.create(
            title="Hard Blocked", seller_id=test_user.id, category=test_category, status=ProductStatus.HARD_BLOCKED
        )
        url = reverse('specific-product', args=[product.id])
        
        response = jwt_client.patch(url, base_data, format='multipart')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_edit_others_product_returns_403(self, jwt_client, test_user, test_category, base_data):
        another_seller = Seller.objects.create_user(username="other", password="pass")
        product = Product.objects.create(
            title="Not Mine", seller=another_seller, category=test_category
        )
        url = reverse('specific-product', args=[product.id])
        
        response = jwt_client.patch(url, base_data, format='multipart')
        assert response.status_code == status.HTTP_403_FORBIDDEN