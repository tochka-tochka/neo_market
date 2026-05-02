from django.http import JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http.request import HttpRequest
from src.api.products.service.main import get_product, create_product, update_product, delete_product, get_all_products, get_categories
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from src.serializes import ProductSerializer


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
    
    def post(self, request: HttpRequest):
        title = request.data.get('title')
        description = request.data.get('description')
        category = request.data.get('category')
        characteristics = request.data.get('characteristics')


        images = request.FILES.getlist('images')

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
            id = create_product(data, images, request.user)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
        
        return JsonResponse({"id": str(id)}, status=201)
    
    def put(self, request, id: str = None):
        title = request.data.get('title')
        description = request.data.get('description')
        category = request.data.get('category')
        characteristics = request.data.get('characteristics')


        images = request.FILES.getlist("images")

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
            update_product(data, images, request.user)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
        
        return JsonResponse({"message": "success"}, status=200)
    
    def delete(self, request: HttpRequest, id: str):
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
        

@method_decorator(csrf_exempt, name='dispatch')
class CategoriesView(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request: HttpRequest):
        try:
            categories = get_categories()
            return JsonResponse({ "categories" : categories }, status=200)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

def get_full_category(_id: uuid.UUID, include_product_count: bool, lang: Literal["ru", "en"]):
    category = get_category(_id)
    if category.parent_id:
        parent_obj = Category.objects.get(id=category.parent_id)
        parent = {
            "id": parent_obj.id,
            "name": parent_obj.value,
            "slug": parent_obj.slug
        }
    else:
        parent = None
    seo = {
        "title": category.seo_title,
        "description": category.seo_description,
        "keywords": []  # TODO
    }
    if include_product_count:
        product_count = Product.objects.filter(category=_id).count()
    else:
        product_count = None
    meta = {}
    return {
        "id": category.id,
        "name": category.value,
        "slug": category.slug,
        "description": category.description,
        "parent": parent,
        "product_count": product_count,
        "seo": seo,
        "meta_tags": meta,
        "image_url": category.image_url,
        "is_active": category.is_active,
        "created_at": category.created_at,
        "updated_at": category.updated_at
    }


@method_decorator(csrf_exempt, name='dispatch')
class CategoryView(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request: HttpRequest, id: uuid.UUID):
        try:
            include_product_count = request.GET.get("include_product_count") == "true"
            lang = request.GET.get("lang", "ru")
            json_cat = get_full_category(id, include_product_count, lang)
            return JsonResponse(json_cat, status=200, safe=False)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
