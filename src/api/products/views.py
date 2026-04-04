import json
import uuid
from django.http import JsonResponse
from django.views import View
from django.http.request import HttpRequest
from src.api.products.service.main import get_product, create_product, update_product, delete_product
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

        return JsonResponse({
            "product": {
                "id": str(id),
                "title": product.title,
                "description": product.description,
                "status": product.status,
                "image": product.image,
            }
        })
    
    def post(self, request: HttpRequest):
        data = json.loads(request.body)
        image = request.FILES.get("image")

        try:
            id = create_product(data, image)
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