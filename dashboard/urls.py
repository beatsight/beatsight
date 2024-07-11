from django.urls import path

from . import views

urlpatterns = [
    path("", views.Detail.as_view({
        'get': 'dashboard',
    }), name="dashboard"),
]
