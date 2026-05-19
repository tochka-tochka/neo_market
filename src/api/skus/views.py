from src.models.product import SKU
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from src.api.skus.service.main import create_sku, update_sku, delete_sku
from src.serializers.skus_serializers import SKUSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from .service.main import BlockedProductException, AccessDenied, SKUNotFound, SKUGotActiveReserbes

@method_decorator(csrf_exempt, name='dispatch')
class SkusView(APIView):
    permission_classes = [IsAuthenticated]

    parser_classes = [JSONParser]

    def post(self, request):
        product_id = request.data.get('product_id')
        name = request.data.get('name')
        if not name:
            return JsonResponse({"errors": "name required"}, status=422)
            
        price = request.data.get('price')
        if not price:
            return JsonResponse({"errors": "price required"}, status=422)
            
        cost_price = request.data.get('cost_price')
        if not cost_price:
            return JsonResponse({"errors": "cost price required"}, status=422)
            
        article = request.data.get('article')
        if not article:
            return JsonResponse({"errors": "article required"}, status=422)
            
        discount = request.data.get('discount')
        characteristics = request.data.get('characteristics')

        images = request.data.get('images')

        data = {
            'name': name,
            'price': int(price),
            'cost_price': int(cost_price),
            'article': article,
            'discount': int(discount or 0),
            'characteristics': characteristics,
            'product_id': product_id,
            'images': images
        }

        serializer = SKUSerializer(data=data)
        if not serializer.is_valid():
            return JsonResponse({"errors": serializer.errors}, status=422)

        try:
            sku = create_sku(data, request.user)
        except AccessDenied as e:
            return JsonResponse({"message": str(e)}, status=403)
        except BlockedProductException as e:
            return JsonResponse({"message": str(e)}, status=403)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

        return JsonResponse(sku, status=201)

    def patch(self, request, id: str):
        name = request.data.get('name')
        price = request.data.get('price')
        cost_price = request.data.get('cost_price')
        discount = request.data.get('discount')
        article = request.data.get('article')
        characteristics = request.data.get('characteristics')
        images = request.data.get('images')

        data = {
            'id': id,
            'name': name,
            'price': price,
            'cost_price': int(cost_price),
            'article': article,
            'discount': int(discount or 0),
            'characteristics': characteristics,
            'images': images
        }

        serializer = SKUSerializer(data=data)
        if not serializer.is_valid():
            return JsonResponse({"errors": serializer.errors}, status=400)

        try:
            sku = update_sku(data, request.user)
        except SKU.DoesNotExist:
            return JsonResponse({"message": "SKU not found"}, status=404)
        except AccessDenied as e:
            return JsonResponse({"message": str(e)}, status=403)
        except BlockedProductException:
            return JsonResponse({"message": "product is hard blocked"}, status=403)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

        return JsonResponse(sku, status=200)

    def delete(self, request, id: str):
        try:
            delete_sku(id, request.user)
        except SKUNotFound as e:
            return JsonResponse({"message" : str(e)}, status=404)
        except SKUGotActiveReserbes as e:
            return JsonResponse({"message" : str(e)}, status=409)
        except AccessDenied as e:
            return JsonResponse({"message" : str(e)}, status=403)
        except BlockedProductException as e:
            return JsonResponse({"message" : str(e)}, status=403)
        except Exception as e:
            return JsonResponse({"message" : str(e)}, status=500)

        return JsonResponse({"ok": True}, status=204)
