from rest_framework.pagination import PageNumberPagination


class MyPaginationClass(PageNumberPagination):

    def get_page_size(self, request):
        page_size = request.query_params.get('page_size', 10)
        return page_size
