from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import ugettext_lazy as _

from .models import *


class CustomAuthForm(AuthenticationForm):
    '''Simple login form'''
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Логин'}))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}))

    error_messages = {
        'invalid_login': _("Пожалуйста, введите правильное имя пользователя и пароль."
                           "Обратите внимание, что оба поля чувствительны к регистру."),
        'inactive': _("Этот аккаунт отключен."),
    }

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username,
                                           password=password)
            if self.user_cache is None:
                self.add_error(
                    'username',
                    self.error_messages['invalid_login'],
                    # code='invalid_login',
                    # params={'username': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data