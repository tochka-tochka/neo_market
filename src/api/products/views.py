import json
import uuid
from django.http import JsonResponse
from django.views import View
from django.http.request import HttpRequest
from src.api.products.service.main import get_product, create_product, create_char, update_product, delete_product, get_all_products, get_categories
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name='dispatch')
class ProductsView(View):
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
        
        properties_str = request.POST.get('chars')
        properties = json.loads(properties_str) if properties_str else {}
        
        image = request.FILES.get('image')

        data = {
            'title': title,
            'description': description,
            'category': category,
        }

        try:
            id = create_product(data, image)

            for char in properties:
                    create_char({
                        "product": id,
                        "name": char['name'],
                        "value": char['value']
                    })
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
        
        return JsonResponse({"id": str(id)}, status=201)
    
    def patch(self, request: HttpRequest):
        data = json.loads(request.body)
        image = request.FILES.get("image")

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
class AllProductsView(View):
    def get(self, request: HttpRequest):
        try:
            products = get_all_products()
            return JsonResponse({ "products" : products }, status=200)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
        
@method_decorator(csrf_exempt, name='dispatch')
class CategoriesView(View):
    def get(self, request: HttpRequest):
        try:
            categories = get_categories()
            return JsonResponse({ "categories" : categories }, status=200)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)