from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:email>/", views.detail, name="detail"),
    path("<str:email>/projects", views.projects, name="projects"),
]
