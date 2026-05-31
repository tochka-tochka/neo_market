import uuid
from collections import defaultdict
from typing import Literal

from django.db.models import Q, Count

from src.api.products.service.category_service import get_category
from src.api.products.service.product_utils import product_filter_query
from src.models import Category, Product
from src.models.category import CategorySEOKeyword, CategoryMetaTag, CategoryFilter


# TODO: lang support
def get_full_category(_id: uuid.UUID, include_product_count: bool, lang: Literal["ru", "en"]):
    category = get_category(_id)
    if category.parent_id:
        parent_obj = Category.objects.get(id=category.parent_id)
        parent = {
            "id": parent_obj.id,
            "name": parent_obj.name,
            "slug": parent_obj.slug
        }
    else:
        parent = None
    seo_keywords = CategorySEOKeyword.objects.filter(category_id=_id)
    seo = {
        "title": category.seo_title,
        "description": category.seo_description,
        "keywords": [kw.name for kw in seo_keywords]
    }
    if include_product_count:
        product_count = Product.objects.filter(category=_id).count()
    else:
        product_count = None
    meta_tags = CategoryMetaTag.objects.filter(category_id=_id)
    meta = {mt.tag: mt.value for mt in meta_tags}
    return {
        "id": category.id,
        "name": category.name,
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


def format_category_filter(category_filter: CategoryFilter):
    d = {
        "slug": category_filter.slug,
        "name": category_filter.name,
        "type": category_filter.type,

    }
    match category_filter.type:
        case "list":
            d["value"] = category_filter.values
        case "range":
            d["min"] = category_filter.values[0]
            d["max"] = category_filter.values[1]
        case "switch":
            pass
    return d


def get_category_filters(category_id: uuid.UUID):
    filters = CategoryFilter.objects.filter(category_id=category_id)
    return {
        "items": [format_category_filter(cf) for cf in filters]
    }


def __serialize_breadcrumb_cat(category: Category):
    return {
        "id": category.id,
        "name": category.name,
        "parent_id": category.parent_id,
        "level": 0,
        "path": "",
        "is_active": category.is_active,
        "created_at": category.created_at,
        "slug": category.slug
    }


def get_category_breadcrumbs(category_id: uuid.UUID) -> list:
    breadcrumbs = [__serialize_breadcrumb_cat(Category.objects.get(id=category_id))]

    while breadcrumbs[0]["parent_id"] is not None:
        prev = Category.objects.get(id=breadcrumbs[0]["parent_id"])
        breadcrumbs.insert(0, __serialize_breadcrumb_cat(prev))
    path = ""
    for i in range(len(breadcrumbs)):
        breadcrumbs[i]["level"] = i
        path += "/" + (breadcrumbs[i]["slug"] or breadcrumbs[i]["name"])
        breadcrumbs[i]["path"] = path
        breadcrumbs[i].pop("slug")

    return breadcrumbs


def category_products_queryset(category_id: uuid.UUID, applied_filters: list[tuple[str, str]]):
    characteristics_filter = Q()
    for filter_name, filter_value in applied_filters:
        characteristics_filter |= Q(characteristics__name=filter_name, characteristics__value=filter_value)

    return Product.objects.filter(characteristics_filter, category_id=category_id)


def get_category_facet(category_id: str, filters: dict[str, list[str]]) -> list:
    filter_query = product_filter_query(filters)
    product_query = Q(category_id=category_id)
    queryset = (Product.objects.filter(product_query & filter_query)
                .values('characteristics__name', 'characteristics__value')
                .annotate(count=Count('id')))

    joined_facets = defaultdict(list)
    for raw_facet_item in queryset:
        joined_facets[raw_facet_item["characteristics__name"]].append({
            "value": raw_facet_item['characteristics__value'],
            "count": raw_facet_item['count']
        })

    return [
        {"name": fname, "values": fvalues}
        for fname, fvalues in joined_facets.items()
    ]
