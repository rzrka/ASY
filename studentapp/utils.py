from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth.mixins import LoginRequiredMixin as MainLoginRequiredMixin
from django.http import HttpResponseForbidden

from mainapp.utils import LoginRequiredMixin as MainLoginRequiredMixin
from mainapp.models import *

USER_GROUP_NAME = 'Students'

class LoginRequiredMixin(MainLoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if (not self.request.user.groups.filter(name=USER_GROUP_NAME).exists()):
            return self.handle_no_permission() 
        return super().dispatch(request, *args, **kwargs)


class LoginSemesterMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        try:
            semester = get_object_or_404(Semester, id=kwargs['semester_id'])
        except Semester.DoesNotExist:
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)


class LoginDisciplineMixin(LoginSemesterMixin):
    def dispatch(self, request, *args, **kwargs):
        try:
            discipline = get_object_or_404(Discipline, id=kwargs['discipline_id'])
        except Semester.DoesNotExist:
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)


class JobMixin(LoginDisciplineMixin):
    def dispatch(self, request, *args, **kwargs):
        try:
            job = get_object_or_404(ControlWork, id=kwargs['job_id'])
        except ControlWork.DoesNotExist:
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)


class HystoryJobMixin(JobMixin):
    def dispatch(self, request, *args, **kwargs):
        history_verification = get_object_or_404(TeleWork, id=kwargs['history_job_id'])
        if not history_verification.is_checked:
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)