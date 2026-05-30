from django.db.models import Sum, Q, Min

from src.api.products.service.product_utils import product_filter_query
from src.models.product import Product, ProductStatus
from src.serializers.product_serializers import PublicProductSerializer, PublicCatalogProductSerializer


class WrongSortParam(Exception):
    pass

class WrongQueryParam(Exception):
    pass


def get_product_public(id: str):
    try:
        product = Product.objects.select_related("category").get(
            id=id, status=ProductStatus.MODERATED, deleted=False
        )
        serializer = PublicProductSerializer(product)

        print(serializer.data["skus"])
        if (
            sum(list(map(lambda sku: sku["active_quantity"], serializer.data["skus"])))
            <= 0
        ):
            raise Product.DoesNotExist

        return serializer.data
    except Product.DoesNotExist as e:
        raise e
    except Exception as e:
        raise Exception(f"failed to get product: {e}")


def get_products_for_catalog(search, category_id, min_price, max_price, seller_id, ids, limit, offset, sort, filters: dict[str, list[str]]):
    query = Q(deleted=False, status=ProductStatus.MODERATED)

    if ids and len(ids) > 0:
        query &= Q(id__in=ids)

    if category_id is not None:
        query &= Q(category=category_id)

    if search:
        query &= (Q(title__icontains=search) | Q(description__icontains=search))

    if min_price is not None:
        try:
            query &= Q(price__gte=int(min_price))
        except ValueError:
            raise WrongQueryParam("min_price must be a number")

    if max_price is not None:
        try:
            query &= Q(price__lte=int(max_price))
        except ValueError:
            raise WrongQueryParam("min_price must be a number")

    if seller_id is not None:
        query &= Q(seller=seller_id)

    if sort is None:
        sort = "created_desc"

    if limit is None:
        limit = 20

    if offset is None:
        offset = 0

    if sort not in ["price_asc", "price_desc", "created_desc", "popular"]:
        raise WrongSortParam("worng sort param")

    if filters:
        query &= product_filter_query(filters)

    order_by_map = {
        "price_asc": "+price",
        "price_desc": "-price",
        "created_desc": "-created_at",
        "popular": "-created_at"
    }
    try:
        total_count = (
            Product.objects.annotate(
                price=Min("skus__price"),
                total_qty=Sum('skus__stock_quantity') - Sum('skus__reserved_quantity')
            )
            .select_related("category")
            .filter(query, deleted=False, status=ProductStatus.MODERATED, total_qty__gt=0)
            .count()
        )
        products = (
            Product.objects.annotate(
                price=Min("skus__price"),
                total_qty=Sum('skus__stock_quantity') - Sum('skus__reserved_quantity')
            )
            .select_related("category")
            .filter(query, deleted=False, status=ProductStatus.MODERATED, total_qty__gt=0)
            .order_by(order_by_map[sort])[offset : offset + limit]
        )
        serializer = PublicCatalogProductSerializer(products, many=True)
        return serializer.data, total_count, limit, offset
    except WrongQueryParam as e:
        raise e
    except WrongSortParam as e:
        raise e
    except Exception as e:
        raise Exception(f"failed to get products: {e}")
