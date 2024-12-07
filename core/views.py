"""
This file is part of Beatsight.

Copyright (C) 2024-2025 Beatsight Ltd.
Licensed under the GNU General Public License v3.0.
"""

from django.conf import settings
from rest_framework.decorators import api_view

from projects.models import Project
from beatsight.utils.response import ok, client_error, server_error

@api_view(['GET'])
def health(request):
    try:
        _ = Project.objects.count()
        return ok('')
    except:
        return server_error('server error')

@api_view(['GET'])
def system_info(request):
    data = {}

    current_projects = Project.objects.count()
    data.update({
        'server_version': settings.SERVER_VERSION,
        'current_projects': current_projects,
    })
    return ok(data)
