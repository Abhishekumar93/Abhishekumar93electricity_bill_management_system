from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
import math


class CustomPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 1000
    page_size_query_param = "page_size"

    def get_paginated_response(self, data):

        dynamic_page_size = self.request.query_params.get("page_size")

        if dynamic_page_size:
            self.page_size = int(dynamic_page_size)

        count = self.page.paginator.count
        total_page = math.ceil(count / self.page_size)

        return Response({
            "count": count,
            "page_count": total_page,
            # "next": self.get_next_link(),
            # "previous": self.get_previous_link(),
            "results": data
        })
