from django.urls import path

from . import views

urlpatterns = [
    path("projects/", views.projects, name="projects"),
    path("projects/export/", views.export_projects, name="export_projects"),
    path("developers/", views.developers, name="developers"),
    path("developers/export/", views.export_developers, name="export_developers"),

]
