from django.urls import path

from . import views

urlpatterns = [
    path("", views.ListCreate.as_view(), name='project-list'),
    path("<str:name>/", views.Detail.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy',
    }), name='project-detail'),
    path("<str:name>/contributors/", views.Detail.as_view({
        'get': 'contributors',
    }), name="project-contributors"),
]
