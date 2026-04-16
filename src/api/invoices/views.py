import json
from django.http import JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http.request import HttpRequest
from src.api.invoices.service.main import create_invoice, delete_invoice, accept_invoice, get_all_invoices
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated


@method_decorator(csrf_exempt, name='dispatch')
class InvoicesView(APIView):
    permission_classes = [IsAuthenticated]
    
    parser_classes = [JSONParser]
    
    def get(self, request):
        try:
            invoices = get_all_invoices(request.user)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

        if invoices is None:
            return JsonResponse({"message": "invoices not found"}, status=404)
        

        return JsonResponse({ "invoices" : invoices })
    
    def post(self, request: HttpRequest):
        items = request.data
        if isinstance(items, str):
            try:
                items = json.loads(items)
            except json.JSONDecodeError:
                items = {}

        try:
            id = create_invoice({ "items": items }, request.user)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
        
        return JsonResponse({"id": str(id)}, status=201)
    
    def delete(self, request: HttpRequest, id: str):
        try:
            delete_invoice(id, request.user)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
        
        return JsonResponse({"message": "success"}, status=200)

@method_decorator(csrf_exempt, name='dispatch')
class InvoiceAcceptView(APIView):
    permission_classes = [IsAuthenticated]
    
    parser_classes = [MultiPartParser, FormParser]
    def post(self, request, id: str):
        try:
            accept_invoice(id, request.user)
        except Exception as e: 
            return JsonResponse({"message": str(e)}, status=500)
        
        return JsonResponse({"message": "success"}, status=200)
