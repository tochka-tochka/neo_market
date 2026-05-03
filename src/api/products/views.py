from django.http import JsonResponse
from django.http.request import HttpRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from src.api.products.service.main import get_product, create_product, update_product, delete_product, get_all_products
from src.serializes import ProductSerializer
from .service.main import AccessDenied, InvalidCategoryId, HardBlockerProduct


@method_decorator(csrf_exempt, name='dispatch')
class ProductsView(APIView):
    permission_classes = [IsAuthenticated]
    
    parser_classes = [MultiPartParser, FormParser]
    
    def get(self, request, id: str):
        try:
            product = get_product(id, request.user)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

        if product is None:
            return JsonResponse({"message": "product not found"}, status=404)
        

        return JsonResponse({ "product" : product })
    
    def post(self, request):

        title = request.data.get('title')
        description = request.data.get('description')

        category = request.data.get('category')
        if not category:
            return JsonResponse({"errors": "category required"}, status=400)

        characteristics = request.data.get('characteristics')


        images = request.FILES.getlist('images')
        if len(images) == 0:
            return JsonResponse({"errors": "images required"}, status=400)

        print(images)

        data = {
            'title': title,
            'description': description,
            'category': category,
            'characteristics': characteristics
        }

        serializer = ProductSerializer(data=data)
        if not serializer.is_valid():
            return JsonResponse({"errors": serializer.errors}, status=400)

        try:
            product = create_product(data, images, request.user)
        except InvalidCategoryId:
            return JsonResponse({"message": "category doesnt exists"}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
        
        return JsonResponse(product, status=201, safe=False)
    
    def patch(self, request, id):
        title = request.data.get('title')
        description = request.data.get('description')
        category = request.data.get('category')
        characteristics = request.data.get('characteristics')


        images = request.FILES.getlist("images")
        if len(images) == 0:
            return JsonResponse({"errors": "images required"}, status=400)

        data = {
            'id': id,
            'title': title,
            'description': description,
            'category': category,
            'characteristics': characteristics
        }

        serializer = ProductSerializer(data=data)
        if not serializer.is_valid():
            return JsonResponse({"errors": serializer.errors}, status=400)

        try:
            updated_product = update_product(data, images, request.user)
        except AccessDenied as e:
            return JsonResponse({"message": str(e)}, status=403)
        except HardBlockerProduct as e:
            return JsonResponse({"message": str(e)}, status=403)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
        
        return JsonResponse(updated_product, status=200)
    
    def delete(self, request, id: str):
        try:
            delete_product(id, request.user)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
        
        return JsonResponse({"message": "success"}, status=200)
    

@method_decorator(csrf_exempt, name='dispatch')
class AllProductsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            products = get_all_products(seller=request.user)
            return JsonResponse({ "products" : products }, status=200)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
