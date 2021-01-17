from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect, reverse
from django.views.generic import View
from django.contrib.auth import authenticate, login
from django.http import HttpResponseForbidden, Http404
from django.contrib.auth.views import LoginView as MainLoginView, LogoutView as MainLogoutView
from django.conf import settings
from django.http import FileResponse

from .forms import CustomAuthForm
from .utils import LoginRequiredMixin

from teacherapp.utils import USER_GROUP_NAME as TEACHER_GROUP_NAME
from studentapp.utils import USER_GROUP_NAME as STUDENT_GROUP_NAME

import os
from django.utils.encoding import uri_to_iri, iri_to_uri

# Проверка логина, переход на страницу работы/авторизации
# Сделать класс от LoginRequiredMixin
def index(request):
	if not request.user.is_authenticated:
		return redirect(reverse('mainapp_login_url'))
	if request.user.groups.filter(name=TEACHER_GROUP_NAME).exists():
		return redirect(reverse('teacherapp_index_url'))
	if request.user.groups.filter(name=STUDENT_GROUP_NAME).exists():
		return redirect(reverse('student_index_url'))
	return render(request, 'base.html')


class LoginView(MainLoginView):
	form_class = CustomAuthForm
	redirect_authenticated_user = True


class LogoutView(MainLogoutView):
	next_page = 'mainapp_login_url'


# /*Добавить проверку?*/
def download_file(request, path):
    # settings.MEDIA_ROOT, 
    file_path = os.path.join(path)
    file_path = '/' + uri_to_iri(file_path)
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'))
        return response
    raise Http404
