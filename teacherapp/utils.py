from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth.mixins import LoginRequiredMixin as MainLoginRequiredMixin
from django.http import HttpResponseForbidden

from mainapp.utils import LoginRequiredMixin as MainLoginRequiredMixin
from mainapp.models import *

USER_GROUP_NAME = 'Teachers'

class LoginRequiredMixin(MainLoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if (not self.request.user.groups.filter(name=USER_GROUP_NAME).exists()):
            return self.handle_no_permission() 
        return super().dispatch(request, *args, **kwargs)


class LoginScheduleRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        try:
            schedule = get_object_or_404(Schedule, id=kwargs['schedule_id'])
            schedule = Schedule.objects.get(id=kwargs['schedule_id'], user__teacher__id=request.user.id)
        except Schedule.DoesNotExist:
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)


class LoginLessonRequiredMixin(LoginScheduleRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        try:
            lesson = get_object_or_404(AuditoryLessons, id=kwargs['lesson_id'])
            lesson = AuditoryLessons.objects.get(id=kwargs['lesson_id'], schedule__user__teacher__id=request.user.id)
        except AuditoryLessons.DoesNotExist:
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)


class LoginAttendanceRequiredMixin(LoginLessonRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        try:
            grade = get_object_or_404(AuditoryLessons, id=kwargs['grade_id'])
            grade = AuditoryAttendance.objects.get(id=kwargs['grade_id'], auditorylessons__schedule__user__teacher__id=request.user.id)
        except AuditoryAttendance.DoesNotExist:
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)


class LoginControlTypeMixin(LoginScheduleRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        grade = get_object_or_404(ControlType, id=kwargs['control_type_id'])
        return super().dispatch(request, *args, **kwargs)


class LoginJobMixin(LoginControlTypeMixin):
    def dispatch(self, request, *args, **kwargs):
        job = get_object_or_404(ControlWork, id=kwargs['job_id'])
        return super().dispatch(request, *args, **kwargs)


class LoginCriterionMixin(LoginJobMixin):
    def dispatch(self, request, *args, **kwargs):
        criterion = get_object_or_404(ControlCriterion, id=kwargs['criterion_id'])
        return super().dispatch(request, *args, **kwargs)
       

class LoginGeneralCriterionMixin(LoginControlTypeMixin):
    def dispatch(self, request, *args, **kwargs):
        criterion = get_object_or_404(ControlCriterion, id=kwargs['criterion_id'])
        return super().dispatch(request, *args, **kwargs)



class LoginVerificationMixin(MainLoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        verification = get_object_or_404(TeleWork, id=kwargs['verification_id'])
        return super().dispatch(request, *args, **kwargs)


class VerificationCheckMixin(LoginVerificationMixin):
    def dispatch(self, request, *args, **kwargs):
        verification = get_object_or_404(TeleWork, id=kwargs['verification_id'])
        if request.POST:
            if verification.is_checked:
                return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)


class VerificationUnCheckMixin(LoginVerificationMixin):
    def dispatch(self, request, *args, **kwargs):
        history_verification = get_object_or_404(TeleWork, id=kwargs['history_verification_id'])
        if not history_verification.is_checked:
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)


class CertificationMixin(LoginScheduleRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        certification = get_object_or_404(Certification, id=kwargs['certification_id'])
        return super().dispatch(request, *args, **kwargs)