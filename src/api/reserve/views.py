import json
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.request import Request
from rest_framework.views import APIView
from src.api.reserve.service.main import NotEnoughQunatity, reserve, unreserve, fulfill, OrderNotFound
from src.permissions import IsService


@method_decorator(csrf_exempt, name="dispatch")
class ReserveView(APIView):
    permission_classes = [IsService]
    parser_classes = [JSONParser]

    def post(self, request: Request):
        try:
            result = reserve(request.data.get("idempotency_key"), request.data.get("order_id"), request.data.get("items"))
            return JsonResponse(result, status=200)
        except NotEnoughQunatity as e:
            return JsonResponse(
                {
                    "code": "RESERVE_CONFLICT",
                    "message": str(e),
                    "details": e.details,
                },
                status=409,
            )
        except Exception as e:
            return JsonResponse({"code": "SERVER_ERROR", "message": str(e)}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class UnreserveView(APIView):
    permission_classes = [IsService]
    parser_classes = [JSONParser]

    def post(self, request: Request):
        try:
            result = unreserve(request.data.get("order_id"), request.data.get("items"))
            return JsonResponse(result, status=200)
        except Exception as e:
            return JsonResponse({"code":"SERVER_ERROR", "message": str(e)}, status=500)

@method_decorator(csrf_exempt, name="dispatch")
class FullfillView(APIView):
    permission_classes = [IsService]
    parser_classes = [JSONParser]

    def post(self, request: Request):
        try:
            result = fulfill(request.data.get("order_id"), request.data.get("items"))
            return JsonResponse(result, status=200)
        except OrderNotFound:
            return JsonResponse({"code": "NOT_FOUND", "message": "order not found"}, status=404)
        except NotEnoughQunatity as e:
            return JsonResponse({"code": "FULFILL_CONFLICT", "message": str(e), "details": e.details}, status=409)
        except Exception as e:
            return JsonResponse({"code": "SERVER_ERROR", "message": str(e)}, status=500)
