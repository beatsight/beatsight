from django.conf import settings
from rest_framework.pagination import PageNumberPagination

from beatsight.utils.response import ok

class CustomPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        return ok({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'per_page': settings.REST_FRAMEWORK['PAGE_SIZE'],
            'results': data
        })
