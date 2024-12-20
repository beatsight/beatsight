from rest_framework.views import exception_handler
from rest_framework.exceptions import NotAuthenticated, PermissionDenied, NotFound
from django.conf import settings
from django.http import Http404
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.contrib.auth import logout, authenticate, login
from django.shortcuts import render, redirect
from django.utils import translation
from django.urls import reverse

from .forms import LoginForm, UserPasswordResetForm, UserSetPasswordForm, UserPasswordChangeForm

def custom_exception_handler(exc, context):
    # Call the default exception handler first to get the standard error response.
    response = exception_handler(exc, context)
    # Now add the custom error response.
    if isinstance(exc, Http404) or isinstance(exc, NotFound):
        custom_response = {'status': 'failed', 'data': None, 'error': str(exc), 'error_code': '404_not_found' }
    elif isinstance(exc, NotAuthenticated):
        custom_response = {'status': 'failed', 'data': None, 'error': exc.default_detail, 'error_code': 'not_authenticated'}
    elif isinstance(exc, PermissionDenied):
        custom_response = {'status': 'failed', 'data': None, 'error': '权限错误，请重试', 'error_code': '430_permission_denied' }
    else:
        custom_response = {'status': 'failed', 'data': None, 'error': exc, 'error_code': '500_internal_server_error' }

    if response is not None:
        response.data = custom_response

    return response

def demo(request):
    user = authenticate(request, username='demo', password='demo')
    if user is not None:
        login(request, user)
        return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        raise Http404

# def set_language(request):
#     user_language = request.GET.get('language', 'en')
#     translation.activate(user_language)
#     request.session[translation.LANGUAGE_SESSION_KEY] = user_language
#     return redirect(request.META.get('HTTP_REFERER', '/'))

# Authentication
class UserLoginView(LoginView):
    template_name = 'accounts/login.html'
    form_class = LoginForm


def logout_view(request):
    logout(request)
    return redirect('/accounts/login/')

class UserPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    form_class = UserPasswordResetForm
    extra_context = {
        'redirect_to': '/accounts/password-reset/',
    }

class UserPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    form_class = UserSetPasswordForm

class UserPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    form_class = UserPasswordChangeForm
    extra_context = {
        'redirect_to': '/accounts/password-change/',
    }
