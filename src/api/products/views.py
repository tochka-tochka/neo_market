import json
import uuid
from django.http import JsonResponse
from django.http import QueryDict
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http.request import HttpRequest
from src.api.products.service.main import get_product, create_product, update_product, delete_product, get_all_products, get_categories
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

def parse_request_data(request: HttpRequest) -> dict:
    if request.method in ('PUT', 'PATCH'):
        if request.POST:
            return request.POST
        try:
            return QueryDict(request.body, encoding=request.encoding)
        except Exception:
            return QueryDict('')
    return request.POST

@method_decorator(csrf_exempt, name='dispatch')
class ProductsView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    def get(self, request: HttpRequest, id: str):
        try:
            product = get_product(id)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

        if product is None:
            return JsonResponse({"message": "product not found"}, status=404)

        return JsonResponse(
            { "product" : product }
        )
    
    def post(self, request: HttpRequest):

        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        
        characteristics = request.POST.get('characteristics')
        
        image = request.FILES.get('image')

        data = {
            'title': title,
            'description': description,
            'category': category,
            'characteristics': characteristics
        }

        try:
            id = create_product(data, image)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
        
        return JsonResponse({"id": str(id)}, status=201)
    
    def put(self, request: HttpRequest, id: str = None):   
        request._load_post_and_files()
        print(f"POST: {request.POST}")

        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        
        characteristics = request.POST.get('characteristics')

        image = request.FILES.get("image")

        data = {
            'id': id,
            'title': title,
            'description': description,
            'category': category,
            'characteristics': characteristics
        }

        try:
            update_product(data, image)
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
    def get(self, request: HttpRequest):
        try:
            products = get_all_products()
            return Response({"products": products}, status=200)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
        
@method_decorator(csrf_exempt, name='dispatch')
class CategoriesView(APIView):
    def get(self, request: HttpRequest):
        try:
            categories = get_categories()
            return JsonResponse({ "categories" : categories }, status=200)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)