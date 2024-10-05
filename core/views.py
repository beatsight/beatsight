from django.conf import settings
from rest_framework.decorators import api_view

from projects.models import Project
from beatsight.utils.response import ok, client_error, server_error
from beatsight.utils import rpc

@api_view(['GET'])
def health(request):
    try:
        _ = Project.objects.count()
        return ok('')
    except:
        return server_error('server error')


@api_view(['GET'])
def get_license(request):
    data = rpc.get_license()
    if not data:
        return server_error("license 无效，请联系管理员。")

    current_projects = Project.objects.count()
    data.update({
        'current_projects': current_projects
    })
    return ok(data)

@api_view(['GET'])
def system_info(request):
    data = rpc.get_license()
    if not data:
        return server_error("license 无效，请联系管理员。")

    current_projects = Project.objects.count()
    data.update({
        'server_version': settings.SERVER_VERSION,
        'current_projects': current_projects,
    })
    return ok(data)
