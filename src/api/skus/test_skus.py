import uuid
import pytest
import json
import pika
from io import BytesIO
from PIL import Image
from django.urls import reverse
from rest_framework import status
from src.models.product import SKU, Category, Product, ProductStatus
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
    image = Image.new("RGB", (100, 100))
    image.save(file_res, "JPEG")
    file_res.name = "test.jpg"
    file_res.seek(0)
    return file_res

@pytest.fixture
def sku_payload(test_category, dummy_image):
    return {
        "name": "test sku",
        "price": 10000000,
        "cost_price": 9000000,
        "active_quantity": 10,
        "images": [dummy_image],
        "characteristics": json.dumps([{"name": "test", "value": "test"}])
    }

@pytest.mark.django_db
class TestSKUAPI:

    def _get_rabbitmq_message(self, queue="moder"):
        connection = pika.BlockingConnection(pika.ConnectionParameters("localhost", 5672))
        channel = connection.channel()
        channel.queue_declare(queue=queue, durable=True, arguments={"x-queue-type": "quorum"})
        
        received_body = None
        def callback(ch, method, properties, body):
            nonlocal received_body
            received_body = json.loads(body.decode())
            ch.stop_consuming()

        channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)
        try:
            connection.process_data_events(time_limit=5)
        except Exception:
            pass
        finally:
            connection.close()
        return received_body

    def test_first_sku_transitions_product_to_moderation(self, jwt_client, test_user, test_category, sku_payload):
        product = Product.objects.create(title="T", category=test_category, seller=test_user, status=ProductStatus.CREATED)
        sku_payload["product_id"] = product.id
        
        response = jwt_client.post(reverse("skus"), sku_payload, format="multipart")
        _ = self._get_rabbitmq_message()
        
        product.refresh_from_db()
        assert response.status_code == status.HTTP_201_CREATED
        assert product.status == ProductStatus.ON_MODERATION

    def test_sku_creation_emits_rabbitmq_event(self, jwt_client, test_user, test_category, sku_payload):
        product = Product.objects.create(title="T", category=test_category, seller=test_user, status=ProductStatus.CREATED)
        sku_payload["product_id"] = product.id
        
        jwt_client.post(reverse("skus"), sku_payload, format="multipart")
        
        msg = self._get_rabbitmq_message()
        assert msg is not None, msg
        assert msg["product_id"] == str(product.id), msg
        assert "idempotency_key" in msg

    def test_adding_sku_to_moderated_product_keeps_status(self, jwt_client, test_user, test_category, sku_payload):
            product = Product.objects.create(
                title="Approved Product", 
                category=test_category, 
                seller=test_user, 
                status=ProductStatus.MODERATED
            )
            sku_payload["product_id"] = product.id
            
            response = jwt_client.post(reverse("skus"), sku_payload, format="multipart")
            
            product.refresh_from_db()
            assert response.status_code == status.HTTP_201_CREATED
            assert product.status == ProductStatus.MODERATED
            
            msg = self._get_rabbitmq_message()
            assert msg is None, "Adding SKU to moderated product should not trigger moderation event"

    def test_cannot_add_sku_to_blocked_product(self, jwt_client, test_user, test_category, sku_payload):
        product = Product.objects.create(title="T", category=test_category, seller=test_user, status=ProductStatus.HARD_BLOCKED)
        sku_payload["product_id"] = product.id
        
        response = jwt_client.post(reverse("skus"), sku_payload, format="multipart")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize("initial_status", [ProductStatus.MODERATED, ProductStatus.BLOCKED])
    def test_edit_sku_triggers_re_moderation(self, jwt_client, test_user, test_category, sku_payload, initial_status):
        product = Product.objects.create(title="T", category=test_category, seller=test_user, status=initial_status)
        sku = SKU.objects.create(name="Old", price=10, cost_price=5, active_quantity=1, product=product)
        
        url = reverse("specific-sku", args=[sku.id])
        sku_payload["product_id"] = product.id
        
        response = jwt_client.patch(url, sku_payload, format="multipart")
        
        product.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert product.status == ProductStatus.ON_MODERATION

    def test_edit_sku_of_hard_blocked_product_returns_403(self, jwt_client, test_user, test_category, sku_payload):
        product = Product.objects.create(title="T", category=test_category, seller=test_user, status=ProductStatus.HARD_BLOCKED)
        sku = SKU.objects.create(name="S", price=10, cost_price=5, active_quantity=1, product=product)
        
        url = reverse("specific-sku", args=[sku.id])
        response = jwt_client.patch(url, sku_payload, format="multipart")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_edit_someone_elses_sku_returns_403(self, jwt_client, test_user, test_category, sku_payload):
        another_user_id = uuid.uuid4()
        another_seller = Seller.objects.create(id=another_user_id, username="test_user_2", password="password123")
        other_product = Product.objects.create(title="Other", category=test_category, seller = another_seller)
        sku = SKU.objects.create(name="S", price=10, cost_price=5, active_quantity=1, product=other_product)
        
        url = reverse("specific-sku", args=[sku.id])
        response = jwt_client.patch(url, sku_payload, format="multipart")
        assert response.status_code == status.HTTP_403_FORBIDDEN