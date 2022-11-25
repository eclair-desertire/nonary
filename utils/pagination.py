from django.core.paginator import Paginator
from django.utils.functional import cached_property
from rest_framework_json_api.pagination import JsonApiPageNumberPagination


class FasterDjangoPaginator(Paginator):
    @cached_property
    def count(self):
        # only select 'id' for counting, much cheaper
        return self.object_list.values('id').count()


class FasterPageNumberPagination(JsonApiPageNumberPagination):
    django_paginator_class = FasterDjangoPaginator
