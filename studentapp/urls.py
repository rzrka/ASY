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
	path('', Index.as_view(), name='student_index_url'),
    path('<int:semester_id>/', StudentDisciplineList.as_view(), name='student_discipline_list_url'),
    path('<int:semester_id>/<int:discipline_id>/', StudentScheduleDetial.as_view(), name='student_schedule_detail_url'),
    path('<int:semester_id>/<int:discipline_id>/lessons/', StudentLessonList.as_view(), name='student_lesson_list_url'),
    path('<int:semester_id>/<int:discipline_id>/lessons/<int:lesson_id>/', StudentLessonDetail.as_view(), name='student_lesson_detail_url'),

    path('<int:semester_id>/<int:discipline_id>/jobs/', StudentJobList.as_view(), name='student_job_list_url'),   
    path('<int:semester_id>/<int:discipline_id>/jobs/<int:job_id>/', StudentJobDetail.as_view(), name='student_job_detail_url'),   
    path('<int:semester_id>/<int:discipline_id>/jobs/<int:job_id>/history/', StudentJobHistoryList.as_view(), name='student_job_history_list_url'),   
    path('<int:semester_id>/<int:discipline_id>/jobs/<int:job_id>/history/<int:history_job_id>/', StudentJobHistoryDetail.as_view(), name='student_job_history_detail_url'),  
    path('<int:semester_id>/<int:discipline_id>/jobs/<int:job_id>/history/<int:history_job_id>/add_comment/', JobHistoryDetailAddComment.as_view(), name='student_job_history_add_comment_url'),    
    path('<int:semester_id>/<int:discipline_id>/jobs/<int:job_id>/history/<int:history_job_id>/delete_comment/', JobHistoryDetailDeleteComment.as_view(), name='student_job_history_delete_comment_url'),    
]


# path('login/', views.LoginView.as_view(), name='mainapp_login_url'),
# path('login/', include('django.contrib.auth.urls'), name='mainapp_login_url', kwargs={"authentication_form":CustomAuthForm}),