import json
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.views import APIView

from src.api.reserve.service.main import NotEnoughQunatity, reserve, unreserve
from src.permissions import IsService


@method_decorator(csrf_exempt, name="dispatch")
class ReserveView(APIView):
    permission_classes = [IsService]
    parser_classes = [JSONParser]

    def post(self, request: Request):
        try:
            result = reserve(request.data.get("idempotency_key"), request.data.get("items"))
            return JsonResponse(result, status=200)
        except NotEnoughQunatity as e:
            return JsonResponse(
                {
                    "reserved": False,
                    "failed_items": [
                        {
                            "sku_id": e.sku_id,
                            "requested": e.requested,
                            "available": e.available,
                            "reason": "INSUFFICIENT_STOCK",
                        }
                    ],
                },
                status=409,
            )
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class UnreserveView(APIView):
    permission_classes = [IsService]
    parser_classes = [JSONParser]

    def post(self, request: Request):
        try:
            result = unreserve(request.data.get("order_id"), request.data.get("items"))
            return JsonResponse(result, status=200)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

# @method_decorator(csrf_exempt, name="dispatch")
# class FullifyView(APIView):
#     permission_classes = [IsService]
#     parser_classes = [JSONParser]

#     def post(self, request: Request):
#         try:
#             fullify(request.data.get("order_id"), request.data.get("items"))
#             return JsonResponse({"ok": True}, status=200)
#         except Exception as e:
#             return JsonResponse({"message": str(e)}, status=500)
