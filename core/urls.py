from django.urls import path

from . import views

urlpatterns = [
    path("license/", views.get_license, name="get_license"),
    path("system-info/", views.system_info, name="system_info"),
]
