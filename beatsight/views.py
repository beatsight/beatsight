from rest_framework.views import exception_handler
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from django.http import Http404
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.contrib.auth import logout
from django.shortcuts import render, redirect

from .forms import LoginForm, UserPasswordResetForm

def custom_exception_handler(exc, context):
    # Call the default exception handler first to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the custom error response.
    if isinstance(exc, Http404):
        custom_response = {'status': 'failed', 'data': None, 'error': 'Resource not found', 'error_code': '404_not_found' }
    elif isinstance(exc, NotAuthenticated):
        custom_response = {'status': 'failed', 'data': None, 'error': exc.default_detail, 'error_code': 'not_authenticated'}
    elif isinstance(exc, PermissionDenied):
        custom_response = {'status': 'failed', 'data': None, 'error': '权限错误，请重试', 'error_code': '430_permission_denied' }
    else:
        custom_response = {'status': 'failed', 'data': None, 'error': 'Internal Server Error', 'error_code': '500_internal_server_error' }

    if response is not None:
        response.data = custom_response

    return response


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

# class UserPasswordResetConfirmView(PasswordResetConfirmView):
#     template_name = 'accounts/password_reset_confirm.html'
#     form_class = UserSetPasswordForm

# class UserPasswordChangeView(PasswordChangeView):
#     template_name = 'accounts/password_change.html'
#     form_class = UserPasswordChangeForm
