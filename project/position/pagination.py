from rest_framework import pagination


class CustomPagination(pagination.LimitOffsetPagination):
    default_limit = 10
    limit_query_param = 'l'
    offset_query_param = 'o'
    max_limit = 50
    order_by = 'created_at'
