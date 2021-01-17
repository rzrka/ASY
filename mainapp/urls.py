"""asy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path, include, re_path

from .views import *
# from .forms import *

urlpatterns = [
	path('', index, name='mainapp_index_url'),
    path('login/', LoginView.as_view(), name='mainapp_login_url'),
    path('logout/', LogoutView.as_view(), name='mainapp_logout_url'),
    path('teacher/', include('teacherapp.urls'), name='mainapp_teacher_url'),
    path('student/', include('studentapp.urls'), name='mainapp_student_url'),
    re_path('download/(?P<path>.*)/', download_file, name='mainapp_download_file_url'),
]


# path('login/', views.LoginView.as_view(), name='mainapp_login_url'),
# path('login/', include('django.contrib.auth.urls'), name='mainapp_login_url', kwargs={"authentication_form":CustomAuthForm}),