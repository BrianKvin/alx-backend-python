from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class MessagePagination(PageNumberPagination):
    """
    Custom pagination class for messages, setting 20 messages per page.
    """
    page_size = 20
    page_size_query_param = 'page_size' # Allows client to specify page size (e.g., ?page_size=10)
    max_page_size = 100 

    def get_paginated_response(self, data):
        """
        Overrides the default response to include page count and total item count.
        This is where 'page.paginator.count' would typically be used.
        """
        return Response({
            'count': self.page.paginator.count,  
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })