from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from device_mngr_auth.common.exceptions import PaginatorsFormatException


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
    page_query_param = 'page'
    invalid_page_message = ('The page does not match !!')
        
    def check_max_page_size(self, page_size_query):
        try:
            if int(page_size_query) > self.max_page_size:
                raise PaginatorsFormatException()
        except:
            raise PaginatorsFormatException({
                'status':400,
                'message':f'Page size should be less than or equal to {self.max_page_size}'
            })
        return page_size_query
        
        
    def paginate_queryset(self, queryset, request, view=None):
        
        page_size_query = request.query_params.get('page_size')
        
        if page_size_query is not None:
            self.page_size = self.check_max_page_size(page_size_query)
            
        return super(self.__class__, self).paginate_queryset(queryset, request, view)
            
    
    
    def get_paginated_response(self, data):
        return Response({
            'status':200,
            'message':'Success',
            'data': {
                'count': self.page.paginator.count,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'page_size': int(self.page_size),
                'total_pages': self.page.paginator.num_pages,
                'page': self.page.number,
                'list': data
            }
        })