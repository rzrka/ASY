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
from django.contrib import admin
from django.urls import path, include
from django.views.generic import View

from .views import *

urlpatterns = [
	path('', Index.as_view(), name='teacherapp_index_url'),
    path('schedules/', Schedule_list.as_view(), name='teacherapp_schedule_list_url'),
    path('schedules/<int:schedule_id>/', Schedule_detail.as_view(), name='teacherapp_schedule_detail_url'),
    path('schedules/<int:schedule_id>/lessons/', Lesson_list.as_view(), name='teacherapp_schedule_lessonsList_url'),
    path('schedules/<int:schedule_id>/lessons/create/', Lesson_create.as_view(), name='teacherapp_lesson_create_url'), #create lesson
    path('schedules/<int:schedule_id>/lessons/<int:lesson_id>/', Lesson_detail.as_view(), name='teacherapp_lesson_detail_url'), #update lesson
    path('schedules/<int:schedule_id>/lessons/<int:lesson_id>/delete/', Lesson_delete.as_view(), name='teacherapp_lesson_delete_url'),
    path('schedules/<int:schedule_id>/lessons/<int:lesson_id>/survey/', Attendance_survey.as_view(), name='teacherapp_lesson_attendance_survey_url'), #update lesson
    path('schedules/<int:schedule_id>/lessons/<int:lesson_id>/student_attendance/', Student_attendance_list.as_view(), name='teacherapp_lesson_student_attendance_url'), #student attendance list
    path('schedules/<int:schedule_id>/lessons/<int:lesson_id>/student_attendance/<int:grade_id>/', Student_attendance_detail.as_view(), name='teacherapp_lesson_student_attendance_detail_url'), #student attendance detail
    path('schedules/<int:schedule_id>/control_types/', Control_types.as_view(), name='teacherapp_control_type_list_url'),
    path('schedules/<int:schedule_id>/control_types/create/', Control_type_create.as_view(), name='teacherapp_control_type_create_url'),
    path('schedules/<int:schedule_id>/control_types/<int:control_type_id>/', Control_type_detail.as_view(), name='teacherapp_control_type_detail_url'),
    path('schedules/<int:schedule_id>/control_types/<int:control_type_id>/criterions/', Control_type_general_criterion_list.as_view(), name='teacherapp_control_type_general_criterion_list_url'),
    path('schedules/<int:schedule_id>/control_types/<int:control_type_id>/criterions/create/', Control_type_general_criterion_create.as_view(), name='teacherapp_control_type_general_criterion_create_url'),
    path('schedules/<int:schedule_id>/control_types/<int:control_type_id>/criterions/<int:criterion_id>/', Control_type_general_criterion_detail.as_view(), name='teacherapp_control_type_general_criterion_detail_url'),
    path('schedules/<int:schedule_id>/control_types/<int:control_type_id>/criterions/<int:criterion_id>/create_subcriterion/', Control_type_general_criterion_create_subcriterion.as_view(), name='teacherapp_control_type_general_criterion_create_subcriterion_url'),
    path('schedules/<int:schedule_id>/control_types/<int:control_type_id>/criterions/<int:criterion_id>/delete/', Control_type_general_criterion_delete.as_view(), name='teacherapp_control_type_general_criterion_delete_url'),

    path('schedules/<int:schedule_id>/control_types/<int:control_type_id>/delete/', Control_type_delete.as_view(), name='teacherapp_control_type_delete_url'),
    path('schedules/<int:schedule_id>/control_types/<int:control_type_id>/jobs/', Control_type_job_list.as_view(), name='teacherapp_control_type_job_list_url'),
    path('schedules/<int:schedule_id>/control_types/<int:control_type_id>/jobs/create/', Control_type_job_create.as_view(), name='teacherapp_control_type_job_create_url'),
    path('schedules/<int:schedule_id>/control_types/<int:control_type_id>/jobs/<int:job_id>/', Control_type_job_detail.as_view(), name='teacherapp_control_type_job_detail_url'),
    path('schedules/<int:schedule_id>/control_types/<int:control_type_id>/jobs/<int:job_id>/delete/', Control_type_job_delete.as_view(), name='teacherapp_control_type_job_delete_url'),
    path('schedules/<int:schedule_id>/control_types/<int:control_type_id>/jobs/<int:job_id>/criterions/', Control_type_criterion_list.as_view(), name='teacherapp_control_type_criterion_list_url'),
    path('schedules/<int:schedule_id>/control_types/<int:control_type_id>/jobs/<int:job_id>/criterions/create/', Control_type_criterion_create.as_view(), name='teacherapp_control_type_criterion_create_url'),
    path('schedules/<int:schedule_id>/control_types/<int:control_type_id>/jobs/<int:job_id>/criterions/<int:criterion_id>/', Control_type_criterion_detail.as_view(), name='teacherapp_control_type_criterion_detail_url'),
    path('schedules/<int:schedule_id>/control_types/<int:control_type_id>/jobs/<int:job_id>/criterions/<int:criterion_id>/create_subcriterion/', Control_type_subcriterion_create.as_view(), name='teacherapp_control_type_subcriterion_create_url'),
    path('schedules/<int:schedule_id>/control_types/<int:control_type_id>/jobs/<int:job_id>/criterions/<int:criterion_id>/delete/', Control_type_criterion_delete.as_view(), name='teacherapp_control_type_criterion_delete_url'),

    path('schedules/<int:schedule_id>/control_types/<int:control_type_id>/write/', Control_type_write_list.as_view(), name='teacherapp_control_type_write_url'),
    path('schedules/<int:schedule_id>/control_types/<int:control_type_id>/write/<int:job_id>/', Control_type_write_job.as_view(), name='teacherapp_job_write_url'),
    path('schedules/<int:schedule_id>/control_types/<int:control_type_id>/write/<int:job_id>/survey/', Control_type_write_survey_job.as_view(), name='teacherapp_job_write_survey_url'),

    path('works_verification/', WorkVerification.as_view(), name='teacherapp_works_verification_url'),
    path('works_verification/<int:verification_id>/', WorkVerificationDetail.as_view(), name='teacherapp_works_verification_detail_url'),
    path('works_verification/<int:verification_id>/history/', WorkVerificationHistory.as_view(), name='teacherapp_works_verification_history_url'),
    path('works_verification/<int:verification_id>/history/<int:history_verification_id>/', WorkVerificationHistoryDetail.as_view(), name='teacherapp_works_verification_history_detail_url'),

    path('works_verification/<int:verification_id>/add_comment/', WorkVerificationAddComment.as_view(), name='teacherapp_works_verification_add_comment_url'),
    path('works_verification/<int:verification_id>/delete_comment/', WorkVerificationDeleteComment.as_view(), name='teacherapp_works_verification_delete_comment_url'),

    path('schedules/<int:schedule_id>/control_types/certifications/', Certification_list.as_view(), name='teacherapp_certification_list_url'),
    path('schedules/<int:schedule_id>/control_types/certifications/create/', Certification_create.as_view(), name='teacherapp_certification_create_url'),
    path('schedules/<int:schedule_id>/control_types/certifications/<int:certification_id>/', Certification_detail.as_view(), name='teacherapp_certification_detail_url'),
    path('schedules/<int:schedule_id>/control_types/certifications/<int:certification_id>/delete/', Certification_delete.as_view(), name='teacherapp_certification_delete_url'),

    path('schedules/<int:schedule_id>/control_types/certifications/write/', Certification_write.as_view(), name='teacherapp_certification_write_redirect_url'),
    path('schedules/<int:schedule_id>/control_types/certifications/write/<int:certification_id>/', Certification_write_detail.as_view(), name='teacherapp_certification_write_url'),
]