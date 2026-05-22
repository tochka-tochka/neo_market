from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from src.api.skus.service.main import create_sku, delete_sku, update_sku
from src.models.product import SKU
from src.serializers.skus_serializers import SKUSerializer

from .service.main import (
    AccessDenied,
    BlockedProductException,
    ProductNotFound,
    SKUGotActiveReserbes,
    SKUNotFound,
)


@method_decorator(csrf_exempt, name="dispatch")
class SkusView(APIView):
    permission_classes = [IsAuthenticated]

    parser_classes = [JSONParser]

    def post(self, request):
        product_id = request.data.get("product_id")
        name = request.data.get("name")
        if not name:
            return JsonResponse(
                {"code": "INVALID_REQUEST", "message": "name is required"}, status=422
            )

        price = request.data.get("price")
        if not price:
            return JsonResponse(
                {"code": "INVALID_REQUEST", "message": "price is required"}, status=422
            )

        cost_price = request.data.get("cost_price")
        if not cost_price:
            return JsonResponse(
                {"code": "INVALID_REQUEST", "message": "cost price is required"},
                status=422,
            )

        article = request.data.get("article")
        if not article:
            return JsonResponse(
                {"code": "INVALID_REQUEST", "message": "article is required"},
                status=422,
            )

        discount = request.data.get("discount")
        characteristics = request.data.get("characteristics")

        images = request.data.get("images")
        if not images:
            return JsonResponse(
                {"code": "INVALID_REQUEST", "message": "image is required"}, status=422
            )

        data = {
            "name": name,
            "price": int(price),
            "cost_price": int(cost_price),
            "article": article,
            "discount": int(discount or 0),
            "characteristics": characteristics,
            "product_id": product_id,
            "images": images,
        }

        serializer = SKUSerializer(data=data)
        if not serializer.is_valid():
            return JsonResponse(
                {"code": "INVALID_REQUEST", "message": serializer.errors}, status=422
            )

        try:
            sku = create_sku(data, request.user)
        except ProductNotFound:
            return JsonResponse(
                {"code": "NOT_FOUND", "message": "Product not found"}, status=404
            )
        except AccessDenied as e:
            return JsonResponse({"code": "FORBIDDEN", "message": str(e)}, status=403)
        except BlockedProductException:
            return JsonResponse(
                {
                    "code": "FORBIDDEN",
                    "message": "Cannot add SKU to hard-blocked product",
                },
                status=403,
            )
        except Exception as e:
            return JsonResponse({"code": "SERVER_ERROR", "message": str(e)}, status=500)

        return JsonResponse(sku, status=201)

    def patch(self, request, id: str):
        name = request.data.get("name")
        price = request.data.get("price")
        cost_price = request.data.get("cost_price")
        discount = request.data.get("discount")
        article = request.data.get("article")
        characteristics = request.data.get("characteristics")
        images = request.data.get("images")

        data = {
            "id": id,
            "name": name,
            "price": price,
            "cost_price": int(cost_price),
            "article": article,
            "discount": int(discount or 0),
            "characteristics": characteristics,
            "images": images,
        }

        serializer = SKUSerializer(data=data)
        if not serializer.is_valid():
            return JsonResponse(
                {"code": "INVALID_REQUEST", "message": serializer.errors}, status=422
            )

        try:
            sku = update_sku(data, request.user)
        except SKU.DoesNotExist:
            return JsonResponse(
                {"code": "NOT_FOUND", "message": "SKU not found"}, status=404
            )
        except AccessDenied:
            return JsonResponse(
                {
                    "code": "NOT_OWNER",
                    "message": "Product does not belong to the authenticated seller",
                },
                status=403,
            )
        except BlockedProductException:
            return JsonResponse(
                {"code": "FORBIDDEN", "message": "Cannot edit hard-blocked product"},
                status=403,
            )
        except Exception as e:
            return JsonResponse({"code": "SERVER_ERROR", "message": str(e)}, status=500)

        return JsonResponse(sku, status=200)

    def delete(self, request, id: str):
        try:
            delete_sku(id, request.user)
        except SKUNotFound as e:
            return JsonResponse(
                {"code": "NOT_FOUND", "message": "SKU not found"}, status=404
            )
        except SKUGotActiveReserbes:
            return JsonResponse(
                {
                    "code": "CONFLICT",
                    "message": "Cannot delete SKU with active reserves",
                },
                status=409,
            )
        except AccessDenied as e:
            return JsonResponse(
                {
                    "code": "NOT_OWNER",
                    "message": "Product does not belong to the authenticated seller",
                },
                status=403,
            )
        except BlockedProductException:
            return JsonResponse(
                {
                    "code": "FORBIDDEN",
                    "message": "Cannot delete SKU of hard-blocked product",
                },
                status=403,
            )
        except Exception as e:
            return JsonResponse({"code": "SERVER_ERROR", "message": str(e)}, status=500)

        return JsonResponse({"ok": True}, status=204)
