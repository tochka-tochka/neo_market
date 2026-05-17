import json
from io import BytesIO

import pika
import pytest
from PIL import Image

from src.models.product import SKU, Category, Product, ProductStatus


@pytest.fixture
def test_category(db):
    return Category.objects.create(
        id="e36e66d9-3c26-4085-a7d7-4be7132a46e5",
        name="Test Category",
        slug="test_category",
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
def base_data(test_category, dummy_image):
    return {
        "title": "test",
        "description": "test",
        "slug": "test",
        "category": str(test_category.id),
        "images": [
            {"url": "/some_bucket/test1.jpg", "ordering": 0},
            {"url": "/some_bucket/test1.jpg", "ordering": 1},
        ],
        "characteristics": [{"name": "test", "value": "test"}],
    }


@pytest.fixture
def product_factory(db, test_user, test_category):
    def _make_product(
        seller=test_user,
        status=ProductStatus.CREATED,
        description="Test Description",
        category=test_category,
        **kwargs,
    ):
        return Product.objects.create(
            title=kwargs.pop("title", "Test Product"),
            description=description,
            seller=seller,
            category=test_category,
            status=status,
            blocking_reason=kwargs.pop("blocking_reason", None),
            **kwargs,
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
        "article": "test",
        "images": [
            {"url": "/some_bucket/test1.jpg", "ordering": 0},
            {"url": "/some_bucket/test1.jpg", "ordering": 1},
        ],
        "characteristics": [{"name": "test", "value": "test"}],
    }


@pytest.fixture
def product_with_skus(product_factory):
    p = product_factory(title="Product with SKU", status=ProductStatus.MODERATED)
    SKU.objects.create(
        product=p, name="sku1", price=100, cost_price=80, active_quantity=10
    )
    SKU.objects.create(
        product=p, name="sku2", price=200, cost_price=150, active_quantity=5
    )
    return p


class BaseTestUtil:
    def get_rabbitmq_message(self, queue_name, timeout=5):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters("localhost", 5672)
        )
        channel = connection.channel()
        channel.queue_declare(
            queue=queue_name, durable=True, arguments={"x-queue-type": "quorum"}
        )

        received_body = None

        def callback(ch, method, properties, body):
            nonlocal received_body
            received_body = json.loads(body.decode())
            ch.stop_consuming()

        channel.basic_consume(
            queue=queue_name, on_message_callback=callback, auto_ack=True
        )
        try:
            connection.process_data_events(time_limit=timeout)
        finally:
            connection.close()
        return received_body

    def send_moder_decision(self, data: dict):
        """
        Отправляет тестовые данные в очередь moder_decisions.
        Используется для имитации ответа от сервиса модерации в тестах.
        """
        connection = pika.BlockingConnection(
            pika.ConnectionParameters("localhost", 5672)
        )
        try:
            channel = connection.channel()

            channel.queue_declare(
                queue="moder_decisions",
                durable=True,
                arguments={"x-queue-type": "quorum"},
            )

            channel.basic_publish(
                exchange="",
                routing_key="moder_decisions",
                body=json.dumps(data),
                properties=pika.BasicProperties(
                    delivery_mode=2, content_type="application/json"
                ),
            )
        finally:
            connection.close()

    def _clear_queues(self):
        self.get_rabbitmq_message("moder", timeout=0.1)
        self.get_rabbitmq_message("b2c", timeout=0.1)
        self.get_rabbitmq_message("moder_decisions", timeout=0.1)


@pytest.fixture
def catalog_products(product_factory):
    p_visible = product_factory(title="Visible Product", status=ProductStatus.MODERATED)
    SKU.objects.create(
        product=p_visible,
        name="sku_vis_1",
        price=100,
        cost_price=80,
        active_quantity=10,
    )

    p_visible_2 = product_factory(
        title="Visible Product 2", status=ProductStatus.MODERATED
    )
    SKU.objects.create(
        product=p_visible_2,
        name="sku_vis_2",
        price=150,
        cost_price=100,
        active_quantity=5,
    )

    p_out_of_stock = product_factory(
        title="Out of Stock", status=ProductStatus.MODERATED
    )
    SKU.objects.create(
        product=p_out_of_stock,
        name="sku_oos",
        price=200,
        cost_price=150,
        active_quantity=0,
    )

    p_hard_blocked = product_factory(
        title="Hard Blocked", status=ProductStatus.HARD_BLOCKED
    )
    SKU.objects.create(
        product=p_hard_blocked,
        name="sku_blocked",
        price=300,
        cost_price=200,
        active_quantity=10,
    )

    p_deleted = product_factory(
        title="Deleted Product", status=ProductStatus.MODERATED, deleted=True
    )
    SKU.objects.create(
        product=p_deleted, name="sku_del", price=400, cost_price=300, active_quantity=10
    )

    p_created = product_factory(title="Created Product", status=ProductStatus.CREATED)
    SKU.objects.create(
        product=p_created, name="sku_new", price=500, cost_price=400, active_quantity=10
    )

    return {
        "visible": p_visible,
        "visible_2": p_visible_2,
        "out_of_stock": p_out_of_stock,
        "hard_blocked": p_hard_blocked,
        "deleted": p_deleted,
        "created": p_created,
    }
