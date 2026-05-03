import json
import uuid
from io import BytesIO
from unittest.mock import MagicMock, patch

import pika
import pytest
from django.urls import reverse
from PIL import Image
from rest_framework import status

from src.models.product import SKU, Category, Product, ProductStatus
from src.models.user import Seller


@pytest.mark.django_db
class TestProductAPI:
    def _first_sku_transitions_product_to_on_moderation(self, jwt_client, test_user):
        category = Category.objects.create(
            id="e36e66d9-3c26-4085-a7d7-4be7132a46e5",
            value="Test Category",
            slug="test_category",
        )

        product = Product.objects.create(
            title="test",
            description="test",
            category=category,
            status=ProductStatus.CREATED,
            seller_id=test_user.id,
        )

        url = reverse("skus")

        images = []
        for _ in range(2):
            file_res = BytesIO()
            image = Image.new("RGB", (100, 100))
            image.save(file_res, "JPEG")
            file_res.name = "test.jpg"
            file_res.seek(0)
            images.append(file_res)

        data = {
            "product_id": product.id,
            "name": "test",
            "price": 10000000,
            "cost_price": 9000000,
            "active_quantity": 10,
            "images": images,
            "characteristics": """[
                {
                    "name": "test",
                    "value": "test"
                }
            ]""",
        }

        response = jwt_client.post(url, data, format="multipart")
        assert response.status_code == status.HTTP_201_CREATED, response.json()

        product = Product.objects.get(id=response.json()["product_id"])

        assert product.status == ProductStatus.ON_MODERATION, response.json()

    def _first_sku_emits_created_event_to_moderation(self, jwt_client, test_user):
        category = Category.objects.create(
            id="e36e66d9-3c26-4085-a7d7-4be7132a46e5",
            value="Test Category",
            slug="test_category",
        )

        product = Product.objects.create(
            title="test",
            description="test",
            category=category,
            status=ProductStatus.CREATED,
            seller_id=test_user.id,
        )
        url = reverse("skus")

        images = []
        for _ in range(2):
            file_res = BytesIO()
            image = Image.new("RGB", (100, 100))
            image.save(file_res, "JPEG")
            file_res.name = "test.jpg"
            file_res.seek(0)
            images.append(file_res)

        data = {
            "product_id": product.id,
            "name": "test",
            "price": 10000000,
            "cost_price": 9000000,
            "active_quantity": 10,
            "images": images,
            "characteristics": """[
                {
                    "name": "test",
                    "value": "test"
                }
            ]""",
        }

        connection = pika.BlockingConnection(
            pika.ConnectionParameters("localhost", 5672)
        )
        channel = connection.channel()
        channel.queue_purge(queue="moder")
        channel.queue_declare(
            queue="moder", durable=True, arguments={"x-queue-type": "quorum"}
        )

        response = jwt_client.post(url, data, format="multipart")
        assert response.status_code == status.HTTP_201_CREATED, response.json()

        received_message_body = None

        def callback(ch, method, properties, body):
            nonlocal received_message_body
            rabbitmq_msg_body = json.loads(body.decode())
            received_message_body = rabbitmq_msg_body
            ch.stop_consuming()

        channel.basic_consume(
            queue="moder", on_message_callback=callback, auto_ack=True
        )
        try:
            connection.process_data_events(time_limit=5)
        except pika.exceptions.ConnectionClosedByBroker:
            pass
        finally:
            connection.close()

        print(received_message_body)
        assert received_message_body is not None, "RabbitMQ message was not received"
        assert received_message_body["idempotency_key"] is not None, (
            received_message_body
        )
        assert received_message_body["product_id"] == str(product.id), (
            received_message_body
        )
        assert received_message_body["seller_id"] == str(test_user.id), (
            received_message_body
        )
        assert received_message_body["date"] is not None, received_message_body

    def _adding_more_sku_dont_trigger_cross_service_events(self, jwt_client, test_user):
        category = Category.objects.create(
            id="e36e66d9-3c26-4085-a7d7-4be7132a46e5",
            value="Test Category",
            slug="test_category",
        )

        product = Product.objects.create(
            title="test",
            description="test",
            category=category,
            status=ProductStatus.MODERATED,
            seller_id=test_user.id,
        )

        url = reverse("skus")

        images = []
        for _ in range(2):
            file_res = BytesIO()
            image = Image.new("RGB", (100, 100))
            image.save(file_res, "JPEG")
            file_res.name = "test.jpg"
            file_res.seek(0)
            images.append(file_res)

        data = {
            "product_id": product.id,
            "name": "test",
            "price": 10000000,
            "cost_price": 9000000,
            "active_quantity": 10,
            "images": images,
            "characteristics": """[
                {
                    "name": "test",
                    "value": "test"
                }
            ]""",
        }

        response = jwt_client.post(url, data, format="multipart")
        assert response.status_code == status.HTTP_201_CREATED, response.json()

        product = Product.objects.get(id=response.json()["product_id"])

        assert product.status == ProductStatus.MODERATED, response.json()

    def _impossible_add_sku_to_blocked_product(self, jwt_client, test_user):
        category = Category.objects.create(
            id="e36e66d9-3c26-4085-a7d7-4be7132a46e5",
            value="Test Category",
            slug="test_category",
        )

        product = Product.objects.create(
            title="test",
            description="test",
            category=category,
            status=ProductStatus.HARD_BLOCKED,
            seller_id=test_user.id,
        )

        url = reverse("skus")

        images = []
        for _ in range(2):
            file_res = BytesIO()
            image = Image.new("RGB", (100, 100))
            image.save(file_res, "JPEG")
            file_res.name = "test.jpg"
            file_res.seek(0)
            images.append(file_res)

        data = {
            "product_id": product.id,
            "name": "test",
            "price": 10000000,
            "cost_price": 9000000,
            "active_quantity": 10,
            "images": images,
            "characteristics": """[
                {
                    "name": "test",
                    "value": "test"
                }
            ]""",
        }

        response = jwt_client.post(url, data, format="multipart")

        assert response.status_code == status.HTTP_403_FORBIDDEN, response.json()

    @patch("pika.BlockingConnection")
    def test_edit_moderated_product_returns_to_on_moderation(
        self, mock_blocking_connection, jwt_client, test_user
    ):
        category = Category.objects.create(
            id="e36e66d9-3c26-4085-a7d7-4be7132a46e5",
            value="Test Category",
            slug="test_category",
        )

        product = Product.objects.create(
            title="test",
            description="test",
            category=category,
            status=ProductStatus.MODERATED,
            seller_id=test_user.id,
        )

        url = reverse("skus")

        images = []
        for _ in range(2):
            file_res = BytesIO()
            image = Image.new("RGB", (100, 100))
            image.save(file_res, "JPEG")
            file_res.name = "test.jpg"
            file_res.seek(0)
            images.append(file_res)

        data = {
            "product_id": product.id,
            "name": "test",
            "price": 10000000,
            "cost_price": 9000000,
            "active_quantity": 10,
            "images": images,
            "characteristics": """[
                {
                    "name": "test",
                    "value": "test"
                }
            ]""",
        }

        response = jwt_client.post(url, data, format="multipart")
        assert response.status_code == status.HTTP_201_CREATED, response.json()

        sku_id = response.json()["id"]

        patch_url = reverse("specific-sku", args=[sku_id])
        data["name"] = "test2"

        mock_connection_instance = mock_blocking_connection.return_value
        mock_channel_instance = mock_connection_instance.channel.return_value

        response = jwt_client.patch(patch_url, data, format="multipart")
        assert response.status_code == status.HTTP_200_OK, response.json()

        product = Product.objects.get(id=response.json()["product_id"])
        assert product.status == ProductStatus.ON_MODERATION, response.json()

        mock_channel_instance.basic_publish.assert_called_once()
        args, kwargs = mock_channel_instance.basic_publish.call_args

        published_message_body = json.loads(kwargs["body"])

        assert published_message_body["idempotency_key"] is not None, (
            published_message_body
        )
        assert published_message_body["product_id"] == str(product.id), (
            published_message_body
        )
        assert published_message_body["seller_id"] == str(test_user.id), (
            published_message_body
        )
        assert published_message_body["date"] is not None, published_message_body

    @patch("pika.BlockingConnection")
    def test_edit_blocked_product_returns_to_on_moderation(
        self, mock_blocking_connection, jwt_client, test_user
    ):
        category = Category.objects.create(
            id="e36e66d9-3c26-4085-a7d7-4be7132a46e5",
            value="Test Category",
            slug="test_category",
        )

        product = Product.objects.create(
            title="test",
            description="test",
            category=category,
            status=ProductStatus.BLOCKED,
            seller_id=test_user.id,
        )

        sku = SKU.objects.create(
            name="test", price=10, cost_price=10, active_quantity=10, product=product
        )

        images = []
        for _ in range(2):
            file_res = BytesIO()
            image = Image.new("RGB", (100, 100))
            image.save(file_res, "JPEG")
            file_res.name = "test.jpg"
            file_res.seek(0)
            images.append(file_res)

        patch_url = reverse("specific-sku", args=[sku.id])
        data = {
            "product_id": product.id,
            "name": "test2",
            "price": 10000000,
            "cost_price": 9000000,
            "active_quantity": 10,
            "images": images,
            "characteristics": """[
                {
                    "name": "test",
                    "value": "test"
                }
            ]""",
        }

        mock_connection_instance = mock_blocking_connection.return_value
        mock_channel_instance = mock_connection_instance.channel.return_value

        response = jwt_client.patch(patch_url, data, format="multipart")
        assert response.status_code == status.HTTP_200_OK, response.json()

        product = Product.objects.get(id=response.json()["product_id"])
        assert product.status == ProductStatus.ON_MODERATION, response.json()

        mock_channel_instance.basic_publish.assert_called_once()
        args, kwargs = mock_channel_instance.basic_publish.call_args

        published_message_body = json.loads(kwargs["body"])

        assert published_message_body["idempotency_key"] is not None, (
            published_message_body
        )
        assert published_message_body["product_id"] == str(product.id), (
            published_message_body
        )
        assert published_message_body["seller_id"] == str(test_user.id), (
            published_message_body
        )
        assert published_message_body["date"] is not None, published_message_body

    def test_edit_hard_blocked_returns_403(self, jwt_client, test_user):
        category = Category.objects.create(
            id="e36e66d9-3c26-4085-a7d7-4be7132a46e5",
            value="Test Category",
            slug="test_category",
        )

        product = Product.objects.create(
            title="test",
            description="test",
            category=category,
            status=ProductStatus.HARD_BLOCKED,
            seller_id=test_user.id,
        )

        sku = SKU.objects.create(
            name="test", price=10, cost_price=10, active_quantity=10, product=product
        )

        images = []
        for _ in range(2):
            file_res = BytesIO()
            image = Image.new("RGB", (100, 100))
            image.save(file_res, "JPEG")
            file_res.name = "test.jpg"
            file_res.seek(0)
            images.append(file_res)

        patch_url = reverse("specific-sku", args=[sku.id])
        data = {
            "product_id": product.id,
            "name": "test2",
            "price": 10000000,
            "cost_price": 9000000,
            "active_quantity": 10,
            "images": images,
            "characteristics": """[
                {
                    "name": "test",
                    "value": "test"
                }
            ]""",
        }

        connection = pika.BlockingConnection(
            pika.ConnectionParameters("localhost", 5672)
        )
        channel = connection.channel()
        channel.queue_purge(queue="moder")
        channel.queue_declare(
            queue="moder", durable=True, arguments={"x-queue-type": "quorum"}
        )

        response = jwt_client.patch(patch_url, data, format="multipart")
        assert response.status_code == status.HTTP_403_FORBIDDEN, response.json()

    def test_others_product_returns_403(self, jwt_client, test_user):
        another_user_id = uuid.uuid4()
        Seller.objects.create(
            id=another_user_id, username="test_user_2", password="password123"
        )
        category = Category.objects.create(
            id="e36e66d9-3c26-4085-a7d7-4be7132a46e5",
            value="Test Category",
            slug="test_category",
        )

        product = Product.objects.create(
            title="test",
            description="test",
            category=category,
            status=ProductStatus.HARD_BLOCKED,
            seller_id=str(another_user_id),
        )

        sku = SKU.objects.create(
            name="test", price=10, cost_price=10, active_quantity=10, product=product
        )

        images = []
        for _ in range(2):
            file_res = BytesIO()
            image = Image.new("RGB", (100, 100))
            image.save(file_res, "JPEG")
            file_res.name = "test.jpg"
            file_res.seek(0)
            images.append(file_res)

        patch_url = reverse("specific-sku", args=[sku.id])
        data = {
            "product_id": product.id,
            "name": "test2",
            "price": 10000000,
            "cost_price": 9000000,
            "active_quantity": 10,
            "images": images,
            "characteristics": """[
                {
                    "name": "test",
                    "value": "test"
                }
            ]""",
        }

        connection = pika.BlockingConnection(
            pika.ConnectionParameters("localhost", 5672)
        )
        channel = connection.channel()
        channel.queue_purge(queue="moder")
        channel.queue_declare(
            queue="moder", durable=True, arguments={"x-queue-type": "quorum"}
        )

        response = jwt_client.patch(patch_url, data, format="multipart")
        assert response.status_code == status.HTTP_403_FORBIDDEN, response.json()
