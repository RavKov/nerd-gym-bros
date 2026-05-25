from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from gymApi.pagination import StandardPagination


class PaginatedAPIView(APIView):
    pagination_class = StandardPagination

    def paginate_response(self, request: Request, queryset, serializer_class) -> Response:
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)
