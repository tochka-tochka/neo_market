from django.http import JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from django.http.request import HttpRequest
from src.api.skus.service.main import create_sku, update_sku
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated


@method_decorator(csrf_exempt, name='dispatch')
class SkusView(APIView):
    permission_classes = [IsAuthenticated]
    
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request: HttpRequest):
        name = request.data.get('name')
        price = request.data.get('price')
        active_quantity = request.data.get('active_quantity')
        characteristics = request.data.get('characteristics')
        product_id = request.data.get('product_id')

        data = {
            'name': name,
            'price': int(price),
            'active_quantity': int(active_quantity),
            'characteristics': characteristics,
            'product_id': product_id
        }

        try:
            id = create_sku(data)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
        
        return JsonResponse({"id": str(id)}, status=201)
    
    def put(self, request):
        id = request.data.get('id')
        name = request.data.get('name')
        price = request.data.get('price')
        active_quantity = request.data.get('active_quantity')
        characteristics = request.data.get('characteristics')

        data = {
            'id': id,
            'name': name,
            'price': price,
            'active_quantity': active_quantity,
            'characteristics': characteristics
        }

        try:
            update_sku(data)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
        
        return JsonResponse({"message": "success"}, status=200)