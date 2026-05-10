from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, OR
from rest_framework.views import APIView
from rest_framework.request import Request

from src.api.products.service.product_service import (
    create_product,
    delete_product,
    get_seller_products,
    get_product,
    update_product,
)

from src.api.products.service.public_product_service import (
    get_product_public,
    get_products_for_catalog
)

from src.models.product import Product
from src.permissions import IsService
from src.serializes import ProductSerializer

from .service.product_service import (
    AccessDenied,
    HardBlockerProduct,
    InvalidCategoryId,
    ProductAlreadyDeleted,
)

from .service.public_product_service import (
    WrongSortParam
)


@method_decorator(csrf_exempt, name="dispatch")
class ProductDetailView(APIView):
    permission_classes = [IsAuthenticated | IsService]
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
            if self.request.method == "GET":
                return [OR(IsAuthenticated(), IsService())]
            return [IsAuthenticated()]

    def get(self, request, id: str):
        is_service = getattr(request, "is_from_service", False)
        try:
            if is_service:
                product = get_product_public(id)
            else:
                product = get_product(id, request.user)
        except Product.DoesNotExist:
            return JsonResponse({"message": "product not found"}, status=404)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

        return JsonResponse({"product": product})

    def patch(self, request, id):
        title = request.data.get("title")
        description = request.data.get("description")
        category = request.data.get("category")
        characteristics = request.data.get("characteristics")

        images = request.FILES.getlist("images")
        if len(images) == 0:
            return JsonResponse({"errors": "images required"}, status=400)

        data = {
            "id": id,
            "title": title,
            "description": description,
            "category": category,
            "characteristics": characteristics,
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
        except ProductAlreadyDeleted as e:
            return JsonResponse({"message": str(e)}, status=400)
        except HardBlockerProduct as e:
            return JsonResponse({"message": str(e)}, status=403)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

        return JsonResponse({"message": "success"}, status=204)


@method_decorator(csrf_exempt, name="dispatch")
class ProductsView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "GET":
            return [OR(IsAuthenticated(), IsService())]
        return [IsAuthenticated()]

    def get(self, request: Request):
        try:
            is_service = getattr(request, "is_from_service", False)
            if is_service:
                ids_param = ids=request.query_params.get("ids", "")
                ids = ids_param.split(",") if ids_param else []
                products, limit, offset = get_products_for_catalog(
                    search=request.query_params.get("search"),
                    category=request.query_params.get("category"),
                    ids=ids,
                    sort=request.query_params.get("sort"),
                    limit=request.query_params.get("limit"),
                    offset=request.query_params.get("offset")
                )
                return JsonResponse({
                    "items": products,
                    "total_count": len(products),
                    "limit": limit,
                    "offset": offset
                }, status=200)
            else:
                products = get_seller_products(seller=request.user)
            return JsonResponse({"products": products}, status=200)
        except WrongSortParam as e:
            return JsonResponse({"message": str(e)}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

    def post(self, request):

        title = request.data.get("title")
        description = request.data.get("description")

        category = request.data.get("category")
        if not category:
            return JsonResponse({"errors": "category required"}, status=400)

        characteristics = request.data.get("characteristics")

        images = request.FILES.getlist("images")
        if len(images) == 0:
            return JsonResponse({"errors": "images required"}, status=400)

        print(images)

        data = {
            "title": title,
            "description": description,
            "category": category,
            "characteristics": characteristics,
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
