from django import forms
from django.contrib.auth.forms import (
    UserCreationForm, AuthenticationForm, PasswordChangeForm, UsernameField, PasswordResetForm, SetPasswordForm
)
from django.utils.translation import gettext_lazy as _

class LoginForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={"class": "focus:shadow-soft-primary-outline text-sm leading-5.6 ease-soft block w-full appearance-none rounded-lg border border-solid border-gray-300 bg-white bg-clip-padding px-3 py-2 font-normal text-gray-700 transition-all focus:border-fuchsia-300 focus:outline-none focus:transition-shadow", "placeholder": "Username"}))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "focus:shadow-soft-primary-outline text-sm leading-5.6 ease-soft block w-full appearance-none rounded-lg border border-solid border-gray-300 bg-white bg-clip-padding px-3 py-2 font-normal text-gray-700 transition-all focus:border-fuchsia-300 focus:outline-none focus:transition-shadow", "placeholder": "Password"}),
    )

class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'focus:shadow-soft-primary-outline text-sm leading-5.6 ease-soft block w-full appearance-none rounded-lg border border-solid border-gray-300 bg-white bg-clip-padding px-3 py-2 font-normal text-gray-700 transition-all focus:border-fuchsia-300 focus:outline-none focus:transition-shadow',
        'placeholder': 'Email'
    }))
