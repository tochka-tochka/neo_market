import re
from collections import defaultdict

from django.db.models import Q
from django.http import QueryDict


def parse_query_filters(filter_param_name: str, query_dict: QueryDict) -> dict[str, list[str]]:
    result = defaultdict(list)
    for key in query_dict:
        r = re.search(filter_param_name + r"\[(\w+)\]", key)
        if r:
            result[r.group(1)].append(query_dict[key])
    print("parsed", query_dict, result)
    return result


def product_filter_query(filters: dict[str, list[str]]) -> Q:
    filters_query = Q()
    for filter_name, filter_values in filters.items():
        filter_query = Q()
        for fval in filter_values:
            filter_query |= Q(characteristics__name=filter_name, characteristics__value=fval)
        filters_query &= filter_query
    return filters_query
