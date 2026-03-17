"""
@ Title:
@ Author: Cathy
@ Time: 2025/7/2 14:25
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response({
            'page': self.page.number,
            'pageSize': self.page.paginator.per_page,
            'pageCount': self.page.paginator.num_pages,
            'itemCount': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'list': data
        })