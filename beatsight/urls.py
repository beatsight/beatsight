"""
URL configuration for beatsight project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib import admin
from django.urls import path, include
# from django.views.i18n import JavaScriptCatalog
# from rest_framework import routers

# from projects import views as proj_views

# router = routers.DefaultRouter()
# router.register(r'projects', views.ProjViewSet)

from . import views

@login_required(login_url='/accounts/login/')
def home(request):
    return redirect(settings.LOGIN_REDIRECT_URL)

urlpatterns = [
    path('', home),

    path('api/core/', include('core.urls')),
    path('api/dashboard/', include('dashboard.urls')),
    path('api/reports/', include('reports.urls')),
    path('api/projects/', include('projects.urls')),
    path('api/developers/', include('developers.urls')),
    path('api/profiles/', include('profiles.urls')),
    path('_admin/', admin.site.urls),

    path('accounts/password-reset/', views.UserPasswordResetView.as_view(), name='password_reset'),
    path('accounts/password-reset-done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    path('accounts/password-reset-confirm/<uidb64>/<token>/',
         views.UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),

    path('accounts/password-change/', views.UserPasswordChangeView.as_view(), name='password_change'),
    path('accounts/password-change-done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'
    ), name="password_change_done"),

    path('accounts/login/', views.UserLoginView.as_view(), name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    # path("accounts/", include("django.contrib.auth.urls")),

    # path('accounts/set_language/', views.set_language, name='set_language'),

    path("accounts/i18n/", include("django.conf.urls.i18n")),
    # path("accounts/jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),

    path('stats/', include('stats.urls')),
]

if settings.ENABLE_DEMO_ACCOUNT:
    urlpatterns += [
        path('accounts/demo/', views.demo),
    ]
