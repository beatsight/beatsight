from django.urls import path

from . import views

urlpatterns = [
    path("me/", views.Detail.as_view({
        'get': 'my_profile',
    }), name="profile-me"),
]
