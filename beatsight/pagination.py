"""
This file is part of Beatsight.

Copyright (C) 2024-2025 Beatsight Ltd.
Licensed under the GNU General Public License v3.0.
"""

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
