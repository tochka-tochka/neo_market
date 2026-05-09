import pytest
import json
from io import BytesIO
from PIL import Image
from src.models.product import Category, Product, ProductStatus, SKU, ProductFieldReport
import pika

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
    def _make_product(seller=test_user, status=ProductStatus.CREATED, **kwargs):
        return Product.objects.create(
            title=kwargs.pop('title', "Test Product"),
            description="Test Description",
            seller=seller,
            category=test_category,
            status=status,
            blocking_reason=kwargs.pop('blocking_reason', None),
            **kwargs
        )
    return _make_product

@pytest.fixture
def product(product_factory):
    return product_factory()

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

@pytest.fixture
def product_with_skus(product_factory):
    p = product_factory(title="Product with SKU")
    SKU.objects.create(product=p, name="sku1", price=100, cost_price=80, active_quantity=10)
    SKU.objects.create(product=p, name="sku2", price=200, cost_price=150, active_quantity=5)
    return p

class BaseTestUtil:
    
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