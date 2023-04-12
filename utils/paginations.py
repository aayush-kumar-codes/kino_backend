from rest_framework.pagination import PageNumberPagination


class MyPaginationClass(PageNumberPagination):
    page_size = 5
