from rest_framework.pagination import PageNumberPagination

from recipes.constants import LIMIT, MAX_PAGE_SIZE, PAGE_SIZE


class PageOrLimitPagination(PageNumberPagination):
    """Класс пагинации, по limit или page."""

    page_size = PAGE_SIZE
    max_page_size = MAX_PAGE_SIZE
    page_size_query_param = LIMIT
