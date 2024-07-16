from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:email>/", views.detail, name="detail"),
    path("<str:email>/contributions", views.contributions, name="contributions"),
    path("<str:email>/contrib_calendar/", views.contrib_calendar, name='contrib_calendar'),
    path("<str:email>/activities/", views.activities, name='activities'),
]
