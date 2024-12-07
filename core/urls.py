from django.urls import path

from . import views

urlpatterns = [
    path("_health/", views.health, name="get_health"),
    path("system-info/", views.system_info, name="system_info"),
]
