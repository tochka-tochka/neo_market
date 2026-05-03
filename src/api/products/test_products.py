import pytest
from django.urls import reverse
from rest_framework import status
from io import BytesIO
from PIL import Image
from src.models.product import Category, Product, ProductStatus
from src.models.user import Seller
import uuid
import pika
import json

@pytest.mark.django_db
class TestProductAPI:
    
    def test_create_product_returns_201(self, jwt_client):
        category = Category.objects.create(
            id="e36e66d9-3c26-4085-a7d7-4be7132a46e5", 
            value="Test Category",
            slug="test_category"
        )
        url = reverse('products')
        
        file_res = BytesIO()
        image = Image.new('RGB', (100, 100))
        image.save(file_res, 'JPEG')
        file_res.name = 'test.jpg'
        file_res.seek(0)

        data = {
            "title": "test",
            "description": "test",
            "category": str(category.id),
            "images": file_res,
            "characteristics": """[
                {
                    "name": "test", 
                    "value": "test"
                }
            ]"""
        }
        
        response = jwt_client.post(url, data, format='multipart')
        
        assert response.status_code == status.HTTP_201_CREATED, response.json()
        assert response.json()['status'] == 'CREATED'
        assert response.json()['skus'] == []

    def test_seller_id_taken_from_jwt(self, test_user, jwt_client):
        category = Category.objects.create(
            id="e36e66d9-3c26-4085-a7d7-4be7132a46e5", 
            value="Test Category",
            slug="test_category"
        )
        url = reverse('products')

        file_res = BytesIO()
        image = Image.new('RGB', (100, 100))
        image.save(file_res, 'JPEG')
        file_res.name = 'test.jpg'
        file_res.seek(0)

        data = {
            "title": "test",
            "description": "test",
            "category": str(category.id),
            "images": file_res,
            "characteristics": """[
                {
                    "name": "test", 
                    "value": "test"
                }
            ]"""
        }

        response = jwt_client.post(url, data, format='multipart')

        assert response.status_code == status.HTTP_201_CREATED, response.json()
        assert response.json()['seller']['id'] == str(test_user.id)

    def test_missing_images_returns_400(self, jwt_client):
        category = Category.objects.create(
            id="e36e66d9-3c26-4085-a7d7-4be7132a46e5", 
            value="Test Category",
            slug="test_category"
        )
        url = reverse('products')

        data = {
            "title": "test",
            "description": "test",
            "category": str(category.id),
            "characteristics": """[
                {
                    "name": "test", 
                    "value": "test"
                }
            ]"""
        }

        response = jwt_client.post(url, data, format='multipart')

        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()

    def test_missing_category_returns_400(self, jwt_client):
        category = Category.objects.create(
            id="e36e66d9-3c26-4085-a7d7-4be7132a46e5", 
            value="Test Category",
            slug="test_category"
        )
        url = reverse('products')
        
        file_res = BytesIO()
        image = Image.new('RGB', (100, 100))
        image.save(file_res, 'JPEG')
        file_res.name = 'test.jpg'
        file_res.seek(0)

        data = {
            "title": "test",
            "description": "test",
            "images": file_res,
            "characteristics": """[
                {
                    "name": "test", 
                    "value": "test"
                }
            ]"""
        }
        
        response = jwt_client.post(url, data, format='multipart')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()

    def test_invalid_category_id_returns_400(self, jwt_client):
        category = Category.objects.create(
            id="e36e66d9-3c26-4085-a7d7-4be7132a46e5", 
            value="Test Category",
            slug="test_category"
        )
        url = reverse('products')
        
        file_res = BytesIO()
        image = Image.new('RGB', (100, 100))
        image.save(file_res, 'JPEG')
        file_res.name = 'test.jpg'
        file_res.seek(0)

        data = {
            "title": "test",
            "description": "test",
            "images": file_res,
            "category": "e36e66d9-3c26-4085-a7d7-4be7132a46e6",
            "characteristics": """[
                {
                    "name": "test", 
                    "value": "test"
                }
            ]"""
        }
        
        response = jwt_client.post(url, data, format='multipart')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
        
    def test_invalid_characteristics_returns_400(self, jwt_client):
        category = Category.objects.create(
            id="e36e66d9-3c26-4085-a7d7-4be7132a46e5", 
            value="Test Category",
            slug="test_category"
        )
        url = reverse('products')
        
        file_res = BytesIO()
        image = Image.new('RGB', (100, 100))
        image.save(file_res, 'JPEG')
        file_res.name = 'test.jpg'
        file_res.seek(0)

        data = {
            "title": "test",
            "description": "test",
            "images": file_res,
            "category": str(category.id),
            "characteristics": """[
                {
                    "name": 10, 
                    "value": 20
                }
            ]"""
        }
        
        response = jwt_client.post(url, data, format='multipart')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()

    def test_edit_moderated_product_returns_to_on_moderation(self, jwt_client, test_user):
        category = Category.objects.create(
            id="e36e66d9-3c26-4085-a7d7-4be7132a46e5", 
            value="Test Category",
            slug="test_category"
        )
        url = reverse('products')
        
        file_res = BytesIO()
        image = Image.new('RGB', (100, 100))
        image.save(file_res, 'JPEG')
        file_res.name = 'test.jpg'
        file_res.seek(0)

        data = {
            "title": "test",
            "description": "test",
            "category": str(category.id),
            "images": file_res,
            "characteristics": """[
                {
                    "name": "test", 
                    "value": "test"
                }
            ]"""
        }
        
        response = jwt_client.post(url, data, format='multipart')

        product_id = response.json()['id']
        
        assert response.status_code == status.HTTP_201_CREATED, response.json()
        assert response.json()['status'] == 'CREATED'
        assert response.json()['skus'] == []

        data['title'] = 'test2'

        patch_url = reverse('specific-product', args=[product_id])
        
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672))
        channel = connection.channel()
        channel.queue_purge(queue='moder')
        channel.queue_declare(
            queue='moder',
            durable=True,
            arguments={'x-queue-type': 'quorum'}
        )
        
        response = jwt_client.patch(patch_url, data, format='multipart')

        assert response.status_code == status.HTTP_200_OK, response.json()
        assert response.json()['status'] == ProductStatus.ON_MODERATION, response.json()

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
        assert received_message_body['product_id'] == product_id, received_message_body
        assert received_message_body['seller_id'] == str(test_user.id), received_message_body
        assert received_message_body['date'] is not None , received_message_body

    def test_edit_blocked_product_returns_to_on_moderation(self, jwt_client, test_user):
        category = Category.objects.create(
            id="e36e66d9-3c26-4085-a7d7-4be7132a46e5", 
            value="Test Category",
            slug="test_category"
        )
        
        product = Product.objects.create(
            title="test",
            description="test",
            category=category,
            status=ProductStatus.BLOCKED,
            seller_id=test_user.id
        )

        url = reverse('specific-product', args=[product.id])

        file_res = BytesIO()
        image = Image.new('RGB', (100, 100))
        image.save(file_res, 'JPEG')
        file_res.name = 'test.jpg'
        file_res.seek(0)

        data = {
            "title": "test",
            "description": "test",
            "category": str(category.id),
            "images": file_res,
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
        
        response = jwt_client.patch(url, data, format='multipart')

        assert response.status_code == status.HTTP_200_OK, response.json()
        assert response.json()['status'] == ProductStatus.ON_MODERATION, response.json()

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

    def test_edit_hard_blocked_returns_403(self, jwt_client, test_user):
        category = Category.objects.create(
            id="e36e66d9-3c26-4085-a7d7-4be7132a46e5", 
            value="Test Category",
            slug="test_category"
        )
        
        product = Product.objects.create(
            title="test",
            description="test",
            category=category,
            status=ProductStatus.HARD_BLOCKED,
            seller_id=test_user.id
        )

        url = reverse('specific-product', args=[product.id])

        file_res = BytesIO()
        image = Image.new('RGB', (100, 100))
        image.save(file_res, 'JPEG')
        file_res.name = 'test.jpg'
        file_res.seek(0)

        data = {
            "title": "test",
            "description": "test",
            "category": str(category.id),
            "images": file_res,
            "characteristics": """[
                {
                    "name": "test", 
                    "value": "test"
                }
            ]"""
        }

        response = jwt_client.patch(url, data, format='multipart')

        assert response.status_code == status.HTTP_403_FORBIDDEN, response.json()

    def test_others_product_returns_403(self, jwt_client, test_user):
        another_user_id = uuid.uuid4()
        Seller.objects.create(
            id=another_user_id,
            username="test_user_2",
            password="password123"
        )
        category = Category.objects.create(
            id="e36e66d9-3c26-4085-a7d7-4be7132a46e5", 
            value="Test Category",
            slug="test_category"
        )
        
        product = Product.objects.create(
            title="test",
            description="test",
            category=category,
            status=ProductStatus.HARD_BLOCKED,
            seller_id=str(another_user_id)
        )

        url = reverse('specific-product', args=[product.id])

        file_res = BytesIO()
        image = Image.new('RGB', (100, 100))
        image.save(file_res, 'JPEG')
        file_res.name = 'test.jpg'
        file_res.seek(0)

        data = {
            "title": "test",
            "description": "test",
            "category": str(category.id),
            "images": file_res,
            "characteristics": """[
                {
                    "name": "test", 
                    "value": "test"
                }
            ]"""
        }

        response = jwt_client.patch(url, data, format='multipart')

        assert response.status_code == status.HTTP_403_FORBIDDEN, response.json()