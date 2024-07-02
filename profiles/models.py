from django.db import models
from rest_framework import serializers as S
from django.contrib.auth.models import User

class DetailSerializer(S.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'is_superuser']
