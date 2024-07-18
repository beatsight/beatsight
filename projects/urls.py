from django.urls import path

from . import views

urlpatterns = [
    path("", views.ListCreate.as_view(), name='project-list'),
    path("activities/", views.ActivityList.as_view(), name='project-activities'),
    path("<str:name>/", views.Detail.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy',
    }), name='project-detail'),
    path("<str:name>/contributors/", views.Detail.as_view({
        'get': 'contributors',
    }), name="project-contributors"),
    path("<str:name>/contrib_calendar/", views.Detail.as_view({
        'get': 'contrib_calendar',
    }), name="project-contrib-calendar"),
    path("<str:name>/activities/", views.Detail.as_view({
        'get': 'activities',
    }), name="project-activities"),
]
