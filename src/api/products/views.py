import json
import uuid
from django.http import JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http.request import HttpRequest
from src.api.products.service.main import get_product, create_product, update_product, delete_product, get_all_products, get_categories
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated


@method_decorator(csrf_exempt, name='dispatch')
class ProductsView(APIView):
    permission_classes = [IsAuthenticated]
    
    parser_classes = [MultiPartParser, FormParser]
    
    def get(self, request, id: str):
        try:
            product = get_product(id, request.user)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

        if product is None:
            return JsonResponse({"message": "product not found"}, status=404)
        

        return JsonResponse({ "product" : product })
    
    def post(self, request: HttpRequest):
        title = request.data.get('title')
        description = request.data.get('description')
        category = request.data.get('category')
        characteristics = request.data.get('characteristics')


        image = request.FILES.get('image')

        print(image)

        data = {
            'title': title,
            'description': description,
            'category': category,
            'characteristics': characteristics
        }

        try:
            id = create_product(data, image, request.user)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
        
        return JsonResponse({"id": str(id)}, status=201)
    
    def put(self, request, id: str = None):
        title = request.data.get('title')
        description = request.data.get('description')
        category = request.data.get('category')
        characteristics = request.data.get('characteristics')


        image = request.FILES.get("image")

        data = {
            'id': id,
            'title': title,
            'description': description,
            'category': category,
            'characteristics': characteristics
        }

        try:
            update_product(data, image, request.user)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
        
        return JsonResponse({"message": "success"}, status=200)
    
    def delete(self, request: HttpRequest, id: str):
        try:
            delete_product(id)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
        
        return JsonResponse({"message": "success"}, status=200)
    

@method_decorator(csrf_exempt, name='dispatch')
class AllProductsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            products = get_all_products(seller=request.user)
            return JsonResponse({ "products" : products }, status=200)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
        

@method_decorator(csrf_exempt, name='dispatch')
class CategoriesView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request: HttpRequest):
        try:
            categories = get_categories()
            return JsonResponse({ "categories" : categories }, status=200)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)