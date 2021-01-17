from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import *
from users.models import CustomUser as User

from teacherapp.utils import USER_GROUP_NAME as TEACHER_GROUP_NAME
from studentapp.utils import USER_GROUP_NAME as STUDENT_GROUP_NAME


'''Hide absolute_name field'''
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('discipline', 'studentgroup', 'semester', 'user')
    # readonly_fields = ('absolute_journal_name',)    
    
    def change_view(self, request, object_id, extra_context=None):
        self.exclude = ('absolute_journal_name',)
        return super(ScheduleAdmin, self).change_view(request, object_id, extra_context)



'''Фильтрация пользователей для Teacher'''
class TeacherAdmin(admin.ModelAdmin):
    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['teacher'].queryset = User.objects.filter(groups__name=TEACHER_GROUP_NAME)
        return super(TeacherAdmin, self).render_change_form(request, context, *args, **kwargs)


'''Фильтрация пользователей для Student'''
class StudentAdmin(admin.ModelAdmin):
    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['student'].queryset = User.objects.filter(groups__name=STUDENT_GROUP_NAME)
        return super(StudentAdmin, self).render_change_form(request, context, *args, **kwargs)



admin.site.register(Semester)
admin.site.register(Discipline)
admin.site.register(StudentGroup)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(EducationalEstablishment)
admin.site.register(Student, StudentAdmin)
admin.site.register(Teacher, TeacherAdmin)


# Модели, к которым доступ не требуется
# admin.site.register(AuditoryLessons)
# admin.site.register(AuditoryAttendance)
# admin.site.register(Comment)
# admin.site.register(File)
# admin.site.register(ControlType)
# admin.site.register(ControlWork)
# admin.site.register(ControlCriterion)
# admin.site.register(ControlScale)
# admin.site.register(ControlScaleTranslate)
# admin.site.register(Control_work_grade)
# admin.site.register(TeleWork)
# admin.site.register(TeleWorkCriterionsComment)
# admin.site.register(TeleWorkCriterions)
# admin.site.register(TeleWorkCriterionsCommentStudent)
# admin.site.register(Certification)
# admin.site.register(Certification_control_work)
# admin.site.register(Certification_control_work_grade)