import pytest
from django.urls import reverse
from rest_framework import status
from io import BytesIO
from PIL import Image
from src.models.product import Category

@pytest.mark.django_db
class TestProductAPI:
    
    def test_create_product_returns_201(self, jwt_client):
        category = Category.objects.create(
            id="e36e66d9-3c26-4085-a7d7-4be7132a46e5", 
            value="Test Category"
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
            value="Test Category"
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
            value="Test Category"
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
            value="Test Category"
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
            value="Test Category"
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
            value="Test Category"
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
            "category": "e36e66d9-3c26-4085-a7d7-4be7132a46e6",
            "characteristics": """[
                {
                    "name": 10, 
                    "value": 20
                }
            ]"""
        }
        
        response = jwt_client.post(url, data, format='multipart')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()