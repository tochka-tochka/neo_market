import json

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.permissions import OR, IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView

from src.api.products.service.product_service import (
    create_product,
    delete_product,
    get_product,
    get_seller_products,
    update_product,
)
from src.api.products.service.public_product_service import (
    get_product_public,
    get_products_for_catalog,
)
from src.models.product import Product
from src.permissions import IsService
from src.serializers.product_serializers import ProductSerializer

from .service.product_service import (
    AccessDenied,
    HardBlockerProduct,
    InvalidCategoryId,
    ProductAlreadyDeleted,
)
from .service.product_utils import parse_query_filters
from .service.public_product_service import WrongSortParam


@method_decorator(csrf_exempt, name="dispatch")
class ProductDetailView(APIView):
    permission_classes = [IsAuthenticated | IsService]
    parser_classes = [JSONParser]

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
        characteristics = json.loads(request.data.get("characteristics") or "[]")

        images = request.data.get("images")
        if len(images) == 0:
            return JsonResponse({"errors": "images required"}, status=422)

        data = {
            "id": id,
            "title": title,
            "description": description,
            "category": category,
            "characteristics": characteristics,
            "images": images,
        }

        serializer = ProductSerializer(data=data)
        if not serializer.is_valid():
            return JsonResponse({"errors": serializer.errors}, status=422)

        try:
            updated_product = update_product(data, request.user)
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
        except Product.DoesNotExist:
            return JsonResponse({"message": "product not found"}, status=404)
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
    parser_classes = [JSONParser]

    def get_permissions(self):
        if self.request.method == "GET":
            return [OR(IsAuthenticated(), IsService())]
        return [IsAuthenticated()]

    def get(self, request: Request):
        try:
            is_service = getattr(request, "is_from_service", False)
            if is_service:
                ids_param = request.query_params.get("ids", "")
                ids = ids_param.split(",") if ids_param else []
                products, limit, offset = get_products_for_catalog(
                    search=request.query_params.get("search"),
                    category=request.query_params.get("category"),
                    ids=ids,
                    sort=request.query_params.get("sort"),
                    limit=request.query_params.get("limit"),
                    offset=request.query_params.get("offset"),
                    filters=parse_query_filters("filters", request.query_params),
                )
                return JsonResponse(
                    {
                        "items": products,
                        "total_count": len(products),
                        "limit": limit,
                        "offset": offset,
                    },
                    status=200,
                )
            else:
                products, limit, offset = get_seller_products(
                    search=request.query_params.get("search"),
                    status=request.query_params.get("status"),
                    limit=request.query_params.get("limit"),
                    offset=request.query_params.get("offset"),
                    seller=request.user,
                    deleted=request.query_params.get("deleted"),
                    filters=parse_query_filters("filters", request.query_params),
                )
            return JsonResponse(
                {
                    "items": products,
                    "total_count": len(products),
                    "limit": limit,
                    "offset": offset,
                },
                status=200,
            )
        except WrongSortParam as e:
            return JsonResponse({"message": str(e)}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

    def post(self, request):
        title = request.data.get("title")
        description = request.data.get("description")
        slug = request.data.get("slug")

        category = request.data.get("category")
        if not category:
            return JsonResponse({"errors": "category required"}, status=422)

        characteristics = request.data.get("characteristics")
        if characteristics is None:
            return JsonResponse({"errors": "characteristics required"}, status=422)
        characteristics = json.loads(characteristics)

        images = request.data.get("images")
        if images is None or len(images) == 0:
            return JsonResponse({"errors": "images required"}, status=422)

        data = {
            "title": title,
            "description": description,
            "slug": slug,
            "category": category,
            "characteristics": characteristics,
            "images": images,
        }

        serializer = ProductSerializer(data=data)
        if not serializer.is_valid():
            return JsonResponse({"errors": serializer.errors}, status=422)

        try:
            product = create_product(data, request.user)
        except InvalidCategoryId:
            return JsonResponse({"message": "category doesnt exists"}, status=422)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

        return JsonResponse(product, status=201, safe=False)
