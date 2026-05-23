from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from src.api.invoices.service.main import (
    AccessDenied,
    ProductNotModerated,
    SKUNotFound,
    create_invoice,
    delete_invoice,
    get_all_invoices,
)


@method_decorator(csrf_exempt, name="dispatch")
class InvoicesView(APIView):
    permission_classes = [IsAuthenticated]

    parser_classes = [JSONParser]

    def get(self, request):
        try:
            invoices, limit, offset = get_all_invoices(
                request.user,
                request.query_params.get("limit"),
                request.query_params.get("offset"),
                request.query_params.get("status"),
            )
        except Exception as e:
            return JsonResponse({"code": "SERVER_ERROR", "message": str(e)}, status=500)

        return JsonResponse({"items": invoices, "total_count": len(invoices), "limit": limit, "offset": offset})

    def post(self, request):
        items = request.data.get("items")
        if not items or len(items) == 0:
            return JsonResponse(
                {"code": "INVALID_REQUEST", "message": "At least one item is required"},
                status=400,
            )

        try:
            invoice = create_invoice({"items": items}, request.user)
        except SKUNotFound:
            return JsonResponse(
                {"code": "NOT_FOUND", "message": "SKU not found"},
                status=404,
            )
        except AccessDenied:
            return JsonResponse(
                {
                    "code": "NOT_OWNER",
                    "message": "One or more SKUs do not belong to the authenticated seller",
                },
                status=403,
            )
        except ProductNotModerated:
            return JsonResponse(
                {
                    "code": "INVALID_REQUEST",
                    "message": "Invoice can only be created for MODERATED products",
                },
                status=400,
            )
        except Exception as e:
            return JsonResponse({"code": "SERVER_ERROR", "message": str(e)}, status=500)

        return JsonResponse(invoice, status=201)

    def delete(self, request, id: str):
        try:
            delete_invoice(id, request.user)
        except Exception as e:
            return JsonResponse({"code": "SERVER_ERROR", "message": str(e)}, status=500)

        return JsonResponse({"message": "success"}, status=200)
