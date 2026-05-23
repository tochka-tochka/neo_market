import uuid

from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView

from src.api.categories.services import get_full_category, get_category_filters,get_category_facet
from src.api.products.service.category_service import get_categories
from src.api.products.service.product_utils import parse_query_filters


@method_decorator(csrf_exempt, name='dispatch')
class CategoriesView(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request: HttpRequest):
        try:
            categories = get_categories()
            return JsonResponse({ "categories" : categories }, status=200)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)


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


@method_decorator(csrf_exempt, name='dispatch')
class CategoryFilterView(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request: HttpRequest, id: uuid.UUID):
        try:
            json_filters = get_category_filters(id)
            return JsonResponse(json_filters, status=200, safe=False)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)


class CatalogFacets(APIView):
    def get(self, request: HttpRequest):
        category_id = request.GET.get("category_id")
        filters = parse_query_filters("filters", request.GET)
        facets = get_category_facet(category_id, filters)
        return JsonResponse(
            {
                "category_id": category_id,
                "facets": facets
            },
            status=200,
            safe=False
        )
