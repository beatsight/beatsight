from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:proj>/", views.detail, name="detail"),
    path("<str:proj>/contributors", views.contributors, name="contributors"),

]
