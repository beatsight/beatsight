from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.decorators import action
from rest_framework.response import Response

from beatsight.utils.response import ok
from .models import DetailSerializer

class Detail(GenericViewSet):
    queryset = User.objects.all()
    serializer_class = DetailSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def my_profile(self, request, *args, **kwargs):
        me = request.user
        return ok(DetailSerializer(me).data)
