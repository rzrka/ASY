from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth.mixins import LoginRequiredMixin as MainLoginRequiredMixin
from django.core.exceptions import PermissionDenied

# from .models import *


class LoginRequiredMixin(MainLoginRequiredMixin):
    # raise_exception = True # If 403
    def handle_no_permission(self):
        if self.raise_exception or self.request.user.is_authenticated:
            raise PermissionDenied(self.get_permission_denied_message())
        return redirect(reverse('mainapp_login_url'))
