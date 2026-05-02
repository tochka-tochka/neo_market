import pytest
import pika
import json
from django.urls import reverse
from rest_framework import status
from io import BytesIO
from PIL import Image
from src.models.product import Category, Product, ProductStatus

@pytest.mark.django_db
class TestProductAPI:
    
    def test_first_sku_transitions_product_to_on_moderation(self, jwt_client, test_user):
        category = Category.objects.create(
            id="e36e66d9-3c26-4085-a7d7-4be7132a46e5", 
            value="Test Category"
        )
        
        product = Product.objects.create(
            title="test",
            description="test",
            category=category,
            status=ProductStatus.CREATED,
            seller_id=test_user.id
        )

        url = reverse('skus')

        images = []
        for _ in range(2):
            file_res = BytesIO()
            image = Image.new('RGB', (100, 100))
            image.save(file_res, 'JPEG')
            file_res.name = 'test.jpg'
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
            ]"""
        }

        response = jwt_client.post(url, data, format='multipart')
        assert response.status_code == status.HTTP_201_CREATED, response.json()
        

        product = Product.objects.get(id=response.json()['product_id'])

        assert product.status == ProductStatus.ON_MODERATION, response.json()

    def test_first_sku_emits_created_event_to_moderation(self, jwt_client, test_user):
        category = Category.objects.create(
            id="e36e66d9-3c26-4085-a7d7-4be7132a46e5",
            value="Test Category"
        )

        product = Product.objects.create(
            title="test",
            description="test",
            category=category,
            status=ProductStatus.CREATED,
            seller_id=test_user.id
        )
        print(product.id)
        url = reverse('skus')

        images = []
        for _ in range(2):
            file_res = BytesIO()
            image = Image.new('RGB', (100, 100))
            image.save(file_res, 'JPEG')
            file_res.name = 'test.jpg'
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
            ]"""
        }

        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672))
        channel = connection.channel()
        channel.queue_purge(queue='moder')
        channel.queue_declare(
            queue='moder',
            durable=True,
            arguments={'x-queue-type': 'quorum'}
        )

        response = jwt_client.post(url, data, format='multipart')
        assert response.status_code == status.HTTP_201_CREATED, response.json()

        received_message_body = None
        
        def callback(ch, method, properties, body):
            nonlocal received_message_body
            rabbitmq_msg_body = json.loads(body.decode())
            received_message_body = rabbitmq_msg_body
            ch.stop_consuming()

        channel.basic_consume(queue='moder',
                                on_message_callback=callback,
                                auto_ack=True
                            )
        try:
            connection.process_data_events(time_limit=5)
        except pika.exceptions.ConnectionClosedByBroker:
            pass
        finally:
            connection.close()

        assert received_message_body is not None, "RabbitMQ message was not received"
        assert received_message_body['idempotency_key'] is not None, received_message_body
        assert received_message_body['product_id'] == str(product.id), received_message_body
        assert received_message_body['seller_id'] == str(test_user.id), received_message_body
        assert received_message_body['date'] is not None , received_message_body

    def test_adding_more_sku_dont_trigger_cross_service_events(self, jwt_client, test_user):
        category = Category.objects.create(
            id="e36e66d9-3c26-4085-a7d7-4be7132a46e5", 
            value="Test Category"
        )
        
        product = Product.objects.create(
            title="test",
            description="test",
            category=category,
            status=ProductStatus.MODERATED,
            seller_id=test_user.id
        )

        url = reverse('skus')

        images = []
        for _ in range(2):
            file_res = BytesIO()
            image = Image.new('RGB', (100, 100))
            image.save(file_res, 'JPEG')
            file_res.name = 'test.jpg'
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
            ]"""
        }

        response = jwt_client.post(url, data, format='multipart')
        assert response.status_code == status.HTTP_201_CREATED, response.json()

        product = Product.objects.get(id=response.json()['product_id'])

        assert product.status == ProductStatus.MODERATED, response.json()

    def test_impossible_add_sku_to_blocked_product(self, jwt_client, test_user):
        category = Category.objects.create(
            id="e36e66d9-3c26-4085-a7d7-4be7132a46e5", 
            value="Test Category"
        )
        
        product = Product.objects.create(
            title="test",
            description="test",
            category=category,
            status=ProductStatus.BLOCKED,
            seller_id=test_user.id
        )

        url = reverse('skus')

        images = []
        for _ in range(2):
            file_res = BytesIO()
            image = Image.new('RGB', (100, 100))
            image.save(file_res, 'JPEG')
            file_res.name = 'test.jpg'
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
            ]"""
        }

        response = jwt_client.post(url, data, format='multipart')

        assert response.status_code == status.HTTP_403_FORBIDDEN, response.json()