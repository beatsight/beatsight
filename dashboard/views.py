from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.decorators import action
from rest_framework.response import Response
from beatsight.utils.response import ok
from projects.models import Project
from developers.models import Developer
from beatsight.consts import ACTIVE, INACTIVE


class Detail(GenericViewSet):
    queryset = Project.objects.all()
    serializer_class = None
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def dashboard(self, request, *args, **kwargs):
        active_proj_cnt = Project.objects.filter(is_active=True).count()
        total_proj_cnt = Project.objects.count()
        active_dev_cnt = Developer.objects.filter(status=ACTIVE).count()
        total_dev_cnt = Developer.objects.count()

        ret = {
            'active_project_count': active_proj_cnt,
            'total_project_count': total_proj_cnt,
            'active_dev_count': active_dev_cnt,
            'total_dev_count': total_dev_cnt,
        }
        return ok(ret)
