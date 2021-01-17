from django.shortcuts import redirect, reverse
from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.contrib.auth.models import User
from django.contrib import messages
from django.core import serializers
from django.db.models import Q, Max, Sum
from datetime import datetime as time
from django.http import HttpResponseRedirect

from .utils import *
from .forms import *
from .fields import *
from mainapp.models import *

class Index(LoginRequiredMixin, View):
    TEMPLATE_INCLUDE_NAME = 'teacherapp/includes/log_entry_main.html'

    def get(self, request):
        semesters = Semester.objects.filter(schedule__user__teacher__id=request.user.id).distinct().order_by('-date_start')
        groups = StudentGroup.objects.filter(schedule__user__teacher__id=request.user.id).distinct().order_by('-year_start_studing', 'name')
        disciplines = Discipline.objects.filter(schedule__user__teacher__id=request.user.id).distinct().order_by('name')
        return render(request, 'teacherapp/log_entry.html', context={
                'semesters': semesters,
                'groups': groups,
                'disciplines': disciplines,
            })

    def post(self, request):
        if request.is_ajax():
            input_data = request.POST
            semesters_dict = {'schedule__user__teacher__id': request.user.id}
            groups_dict = {'schedule__user__teacher__id': request.user.id}
            disciplines_dict = {'schedule__user__teacher__id': request.user.id}
            # schedule__user__id
            if input_data['Semester']:
                semesters_dict['id'] = input_data['Semester']
                groups_dict['schedule__semester__id'] = input_data['Semester']
                disciplines_dict['schedule__semester__id'] = input_data['Semester']
            if input_data['StudentGroup']:
                semesters_dict['schedule__studentgroup__id'] = input_data['StudentGroup']
                groups_dict['id'] = input_data['StudentGroup']
                disciplines_dict['schedule__studentgroup__id'] = input_data['StudentGroup']
            if input_data['Discipline']:
                semesters_dict['schedule__discipline__id'] = input_data['Discipline']
                groups_dict['schedule__discipline__id'] = input_data['Discipline']
                disciplines_dict['id'] = input_data['Discipline']
                
            semesters = Semester.objects.filter(**semesters_dict).distinct().order_by('-date_start')
            groups = StudentGroup.objects.filter(**groups_dict).distinct().order_by('-year_start_studing', 'name')
            disciplines = Discipline.objects.filter(**disciplines_dict).distinct().order_by('name')

            if semesters.count()==1 and groups.count()==1 and disciplines.count()==1:
                schedule = get_object_or_404(Schedule
                , discipline__id=disciplines[0].id
                , studentgroup__id=groups[0].id
                , user__teacher__id = request.user.id
                , semester__id=semesters[0].id)
                return JsonResponse({
                    'redirect': schedule.get_absolute_url(), # ссылка на новую страницу на новую страницу
                }) 

            main_block = render(request, self.TEMPLATE_INCLUDE_NAME, context={
                'semesters': semesters,
                'groups': groups,
                'disciplines': disciplines,
            })
            return HttpResponse(main_block)
        else:
            return JsonResponse({
                'error': 'Only authenticated users'
                }, status=404)


class Schedule_list(LoginRequiredMixin, View):
    def get(self, request):
        schedules = Schedule.objects.filter(user__teacher__id=request.user.id).order_by(
            '-semester__date_start',
            'studentgroup__name',
            )
        return render(request, 'teacherapp/schedule_list.html', context={
            'schedules': schedules,
        })


def UpdateAttendance(schedule):
    students = Student.objects.filter(studentgroup__schedule__id=schedule.id).distinct().order_by('version_in_group')
    for student in students:
        userLessons = AuditoryLessons.objects.filter(schedule__id=schedule.id, auditoryAttendance__student = student) # занятия, которые есть в бд
        for lesson in AuditoryLessons.objects.filter(schedule__id=schedule.id): # все занятия по данному schedule_id
            if not lesson in userLessons: # если урока нет в уроках, то создать с "Неизвестно"
                AuditoryAttendance.objects.create(grade='?', student=student, auditorylessons=lesson)


'''Перевод из процентов в оценку (мб изменить потом)'''
def get_grade_from_procent(procent):
    if not procent:
        procent = 0
    procent = procent * 5.0 / 100.0
    if procent * 10 / 1 % 10 == 5:
        procent += 0.1
    procent = round(procent)
    return max(procent,2)


class Schedule_detail(LoginScheduleRequiredMixin, View):
    def get_attendance_elements(self, schedule):
        schedule__id = schedule.id
        students = Student.objects.filter(studentgroup__schedule__id=schedule.id).distinct().order_by('version_in_group')
        elements = []
        for student in students:
            attendance = {}
            grades = AuditoryAttendance.objects.filter(student=student, auditorylessons__schedule__id = schedule__id).order_by('auditorylessons__lessons_number')
            total_count = grades.count()
            total_count = total_count if total_count else 1
            skips_count = grades.filter(Q(grade='нб.')| Q(grade='нб.(ув.)') ).count()
            bad_skips_count = grades.filter(grade='нб.').count()
            attendance['user'] = student.student
            attendance['grades'] = grades
            attendance['skips'] = ("{skips_count} ({proc}%)".format(
                    skips_count = bad_skips_count,
                    proc = round(bad_skips_count*100/total_count, 2),
                ),
                get_grade_from_procent(100-round(bad_skips_count*100/total_count, 2))
            )
            attendance['normal_skips'] = ("{skips_count} ({proc}%)".format(
                    skips_count = skips_count,
                    proc = round(skips_count*100/total_count, 2),
                ),
                get_grade_from_procent(100-round(skips_count*100/total_count))
            )
            elements.append(attendance)
        return elements

    def get_jobs_elements(self, schedule):
        schedule__id = schedule.id
        students = Student.objects.filter(studentgroup__schedule__id=schedule.id).distinct().order_by('version_in_group')
        elements = {}
        for student in students:
            grades = Control_work_grade.objects.filter(student=student, controlwork__control_type__schedule__id=schedule__id).order_by('controlwork__control_type__name', 'controlwork__work_number')
            elements[student.id] = grades
        return elements
        
    def get(self, request, schedule_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        attendance_elements = self.get_attendance_elements(schedule)
        jobs_elements = self.get_jobs_elements(schedule)
        return render(request, 'teacherapp/schedule_detail.html', context={
            'schedule': schedule,
            'attendance_elements': attendance_elements,
            'jobs_elements': jobs_elements,
        })


class Lesson_list(LoginScheduleRequiredMixin, View):
    def get(self, request, schedule_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        lessons = AuditoryLessons.objects.filter(schedule__id=schedule_id).order_by('lessons_number', 'date')
        return render(request, 'teacherapp/lesson_list.html', context= {
            'schedule': schedule,
            'lessons': lessons,
        }) 


class Lesson_create(LoginScheduleRequiredMixin, View):
    def get(self, request, schedule_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        lesson_num = AuditoryLessons.objects.filter(schedule=schedule).aggregate(Max('lessons_number'))['lessons_number__max']
        lesson_num = (lesson_num if lesson_num else 0) + 1
        bound_form = LessonForm(initial={'schedule': schedule, 'lessons_number':lesson_num})
        
        return render(request, 'teacherapp/lesson_create.html', context={
            'form': bound_form,
            'schedule': schedule,
        })

    def post(self, request, schedule_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        bound_form = LessonForm(request.POST)
        if bound_form.is_valid():
            new_obj = bound_form.save()
            UpdateAttendance(schedule) 
            messages.success(request, 'Новое занятие создано!')
            return redirect(new_obj)
        return render(request, 'teacherapp/lesson_create.html', context={
            'form': bound_form,
            'schedule': schedule,
        })


class Lesson_detail(LoginLessonRequiredMixin, View):        # update
    def get(self, request, schedule_id, lesson_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        lesson = get_object_or_404(AuditoryLessons, id=lesson_id)
        bound_form = LessonForm(instance=lesson)
        bound_forms = []
        for attend in AuditoryAttendance.objects.filter(auditorylessons=lesson).order_by('student__version_in_group'):
            bound_forms.append(AuditoryAttendanceForm(instance=attend, prefix=attend.student.id))
        return render(request, 'teacherapp/lesson_detail.html', context = {
            'form': bound_form,
            'auditorylessons': lesson,
            'grades': bound_forms,
            'lesson': lesson,
            'schedule': schedule,
        })

    def post(self, request, schedule_id, lesson_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        lesson = get_object_or_404(AuditoryLessons, id=lesson_id)
        bound_form = LessonForm(request.POST, instance=lesson)
        bound_forms = []
        for attend in AuditoryAttendance.objects.filter(auditorylessons=lesson).order_by('student__version_in_group'):
            bound_forms.append(AuditoryAttendanceForm(request.POST, instance=attend, prefix=attend.student.id))
        if bound_form.is_valid():
            new_obj = bound_form.save()
            for grade_form in bound_forms:
                grade_form.save()
            messages.success(request, 'Информация о занятии обновлена!')
            return redirect(new_obj)
        return render(request, 'teacherapp/lesson_detail.html', context={
            'form': bound_form,
            'auditorylessons': lesson,
            'grades': bound_forms,
            'lesson': lesson,
            'schedule': schedule,
        })


class Lesson_delete(LoginLessonRequiredMixin, View):
    def post(self, request, schedule_id, lesson_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        lesson = get_object_or_404(AuditoryLessons, id=lesson_id)
        lesson.delete()
        messages.success(request, 'Занятие успешно удалено!')
        return redirect(schedule.get_absolute_url())


class Attendance_survey(LoginLessonRequiredMixin, View):
    def get(self, request, schedule_id, lesson_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        lesson = get_object_or_404(AuditoryLessons, id=lesson_id)
        bound_forms = []
        for attend in AuditoryAttendance.objects.filter(auditorylessons=lesson).order_by('student__version_in_group'):
            bound_forms.append(AuditoryAttendanceForm(instance=attend, prefix=attend.student.id))
        return render(request, 'teacherapp/lesson_attendance_survey.html', context={
            'schedule':schedule,
            'lesson': lesson,
            'grades': bound_forms,
        })

    def post(self, request, schedule_id, lesson_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        lesson = get_object_or_404(AuditoryLessons, id=lesson_id)
        for attend in AuditoryAttendance.objects.filter(auditorylessons=lesson).order_by('student__version_in_group'):
            new_form = AuditoryAttendanceForm(request.POST, instance=attend, prefix=attend.student.id)
            new_form.save()
        messages.success(request, 'Информация о занятии обновлена!')
        return redirect(lesson.get_absolute_url())


class Student_attendance_list(LoginLessonRequiredMixin, View):
    def get (self, request, schedule_id, lesson_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        lesson = get_object_or_404(AuditoryLessons, id=lesson_id)
        grades = AuditoryAttendance.objects.filter(auditorylessons=lesson).order_by('student__version_in_group')
        return render(request, 'teacherapp/attendance_list.html', context={
            'schedule':schedule,
            'lesson': lesson,
            'grades': grades,
        })


class Student_attendance_detail(LoginLessonRequiredMixin, View):
    def get(self, request, schedule_id, lesson_id, grade_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        lesson = get_object_or_404(AuditoryLessons, id=lesson_id)
        grade = get_object_or_404(AuditoryAttendance, id=grade_id)
        bound_form_attendance = AuditoryAttendanceForm(instance=grade, prefix='attendance')
        bound_form_comment = AttendanceCommentForm(initial={'attendance': grade, 'author': request.user}, 
            use_required_attribute=False,
            prefix='comment')
        bound_form_file = AttendanceFileForm(use_required_attribute=False, prefix='file_form')
        for comment in grade.comments.all().filter(~Q(author=request.user)):
            comment.is_readed = True
            comment.save()
        return render(request, 'teacherapp/attendance_detail.html', context={
            'schedule':schedule,
            'lesson': lesson,
            'grade': grade,
            'form': bound_form_attendance,
            'form_comment': bound_form_comment,
            'form_file': bound_form_file,
        })

    def post(self, request, schedule_id, lesson_id, grade_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        lesson = get_object_or_404(AuditoryLessons, id=lesson_id)
        grade = get_object_or_404(AuditoryAttendance, id=grade_id)
        bound_form_attendance = AuditoryAttendanceForm(request.POST, instance=grade, prefix='attendance')
        bound_form_comment = AttendanceCommentForm(request.POST, 
            initial={'attendance': grade, 'author': request.user},
            use_required_attribute=False,
            prefix='comment')
        bound_form_file = AttendanceFileForm(request.POST, request.FILES,
            use_required_attribute=False, prefix='file_form')
        if bound_form_attendance.is_valid():
            attendance = bound_form_attendance.save()
            messages.success(request, 'Информация о занятии обновлена!')
        if 'comment_submit' in request.POST:                                # если нажал на кнопку отправить комментарий
            if bound_form_comment.is_valid():
                new_comment = bound_form_comment.save()
                messages.success(request, 'Комментарий добавлен!')
                bound_form_comment = AttendanceCommentForm(
                    initial={'attendance': grade, 'author': request.user},
                    use_required_attribute=False, prefix='comment')
                if bound_form_file.is_valid():
                    new_file = bound_form_file.save()
                    new_comment.files.add(new_file) # связывание комментария и файла
                    messages.success(request, 'Файл отправлен!')
            bound_form_file = AttendanceFileForm(use_required_attribute=False, prefix='file_form')
        else:
            bound_form_comment = AttendanceCommentForm(
                initial={'attendance': grade, 'author': request.user},
                use_required_attribute=False, prefix='comment')
            bound_form_file = AttendanceFileForm(use_required_attribute=False, prefix='file_form')
        return render(request, 'teacherapp/attendance_detail.html', context={
            'schedule':schedule,
            'lesson': lesson,
            'grade': grade,
            'form': bound_form_attendance,
            'form_comment': bound_form_comment,
            'form_file': bound_form_file,
        })


class Control_types(LoginScheduleRequiredMixin, View):
    def get(self, request, schedule_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        controltypes = ControlType.objects.filter(schedule=schedule).order_by('name')
        workweights = {}
        for controltype in controltypes:
            for work in ControlWork.objects.filter(control_type=controltype):
                workweights[work.id]=ControlTypesWorkWeight(instance=work, prefix=work.id)
        certifications = Certification.objects.filter(schedule=schedule).order_by('number')
        return render(request, 'teacherapp/control_type_list.html', context={
            'schedule': schedule,
            'controltypes': controltypes,
            'workweights': workweights,
            'certifications': certifications,
        })

    def post(self, request, schedule_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        controltypes = ControlType.objects.filter(schedule=schedule).order_by('name')
        is_success = True
        workweights = {}
        for controltype in controltypes:
            for work in ControlWork.objects.filter(control_type=controltype):
                work_form = ControlTypesWorkWeight(request.POST, instance=work, prefix=work.id)
                if work_form.is_valid():
                    work_form.save()
                else:
                    is_success = False
                workweights[work.id] = work_form
        if is_success:
            messages.success(request, 'Информация о видах контроля обновлена!')
        certifications = Certification.objects.filter(schedule=schedule).order_by('number')
        return render(request, 'teacherapp/control_type_list.html', context={
            'schedule': schedule,
            'controltypes': controltypes,
            'workweights': workweights,
            'certifications': certifications,
        })


class Control_type_create(LoginScheduleRequiredMixin, View):
    def get(self, request, schedule_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        predefined_names_list = ControlType.PREDEFINDED_NAMES
        predefined_names_scales = ControlScale.DIMENSION_CHOICES
        form = ControlTypeCreateForm(data_list=predefined_names_list,
            initial={'schedule': schedule},
            prefix='control_type_create')

        form.fields["lesson"].queryset = AuditoryLessons.objects.filter(Q(schedule=schedule) & ~Q(control_type__in=ControlType.objects.all())).order_by('lessons_number')
        return render(request, 'teacherapp/control_type_create.html', context={
            'schedule': schedule,
            'form': form,
        })

    def post(self, request, schedule_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        predefined_names_list = ControlType.PREDEFINDED_NAMES
        form = ControlTypeCreateForm(request.POST, data_list=predefined_names_list,
            initial={'schedule': schedule},
            prefix='control_type_create')
        if form.is_valid():
            new_form = form.save()
            messages.success(request, 'Новый вид контроля создан!')
            return redirect(new_form)         
        form.fields["lesson"].queryset = AuditoryLessons.objects.filter(Q(schedule=schedule) & ~Q(control_type__in=ControlType.objects.all())).order_by('lessons_number')
        return render(request, 'teacherapp/control_type_create.html', context={
            'schedule': schedule,
            'form': form,
        })


class Control_type_detail(LoginControlTypeMixin, View):  # при изменении have_general_criterions очищать критерии
    def get(self, request, schedule_id, control_type_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        control_type = get_object_or_404(ControlType, id=control_type_id)
        predefined_names_list = ControlType.PREDEFINDED_NAMES
        reverse_criterions_href = reverse("teacherapp_control_type_general_criterion_list_url", 
            kwargs={
                "schedule_id": schedule.id, 
                'control_type_id': control_type.id,
                })
        form = ControlTypeCreateForm(data_list=predefined_names_list,
            instance=control_type,
            prefix='control_type_detail')
        if control_type.have_general_criterions: # есть общие критерии
            form.fields['have_general_criterions'].widget = GeneralCriterions_link(
                old_form=form.fields['have_general_criterions'].widget,
                href=reverse_criterions_href,
            )
        queryset = AuditoryLessons.objects.filter(Q(schedule=schedule) & ~Q(control_type__in=ControlType.objects.all())).order_by('lessons_number')
        queryset |= AuditoryLessons.objects.filter(control_type=control_type)
        form.fields["lesson"].queryset = queryset
        return render(request, 'teacherapp/control_type_detail.html', context={
            'schedule': schedule,
            'control_type': control_type,
            'form': form,
        })

    def post(self, request, schedule_id, control_type_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        control_type = get_object_or_404(ControlType, id=control_type_id)
        predefined_names_list = ControlType.PREDEFINDED_NAMES
        reverse_criterions_href = reverse("teacherapp_control_type_general_criterion_list_url", 
            kwargs={
                "schedule_id": schedule.id, 
                'control_type_id': control_type.id,
                })
        form = ControlTypeCreateForm(
            request.POST, 
            data_list=predefined_names_list,
            instance=control_type,
            prefix='control_type_detail')
        ## начало сохранения
        if form.is_valid():
            new_form = form.save()
            messages.success(request, 'Информация о типе контроля успешно изменена')
        ## конец
        if form.instance.have_general_criterions:
            form.fields['have_general_criterions'].widget = GeneralCriterions_link(
                old_form=form.fields['have_general_criterions'].widget,
                href=reverse_criterions_href,
            )
        queryset = AuditoryLessons.objects.filter(Q(schedule=schedule) & ~Q(control_type__in=ControlType.objects.all())).order_by('lessons_number')
        queryset |= AuditoryLessons.objects.filter(control_type=control_type)
        form.fields["lesson"].queryset = queryset
        return render(request, 'teacherapp/control_type_detail.html', context={
            'schedule': schedule,
            'control_type': control_type,
            'form': form,
        })


class Control_type_delete(LoginControlTypeMixin, View):
    def post(self, request, schedule_id, control_type_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        control_type = get_object_or_404(ControlType, id=control_type_id)
        control_type.delete()
        messages.success(request, 'Тип контроля успешно удален!')
        return redirect(reverse("teacherapp_schedule_detail_url", kwargs={
            "schedule_id": schedule.id, 
        }))


class Control_type_job_list(LoginControlTypeMixin, View):
    def get(self, request, schedule_id, control_type_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        control_type = get_object_or_404(ControlType, id=control_type_id)

        jobs = ControlWork.objects.filter(control_type=control_type).order_by('work_number')
        return render(request, 'teacherapp/jobs_list.html', context={
            'schedule': schedule,
            'control_type': control_type,
            'jobs': jobs,
        })


def UpdateJobGrades(schedule):
    students = Student.objects.filter(studentgroup__schedule__id=schedule.id).distinct().order_by('version_in_group')
    for student in students:
        userJobs = ControlWork.objects.filter(control_type__schedule__id=schedule.id, control_work_grades__student=student) # работы, которые есть в бд
        for job in ControlWork.objects.filter(control_type__schedule__id=schedule.id):
            if not job in userJobs:
                Control_work_grade.objects.create(grade=None, student=student, controlwork=job)


class Control_type_job_create(LoginControlTypeMixin, View):
    def get(self, request, schedule_id, control_type_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        control_type = get_object_or_404(ControlType, id=control_type_id)
        job_num = ControlWork.objects.filter(control_type=control_type).aggregate(Max('work_number'))['work_number__max']
        job_num = (job_num if job_num else 0) + 1
        
        form = JobForm(
            initial={
                'control_type': control_type,
                'work_number': job_num,
            },
            prefix='job_main_form_create',
        )
        scale_form = ControlTypeScale(
            data_list=ControlScale.DIMENSION_CHOICES, 
            prefix='control_type_scale_create',
            )
        scale_translate_form = ControlTypeScaleTranslate(
            prefix='control_type_scale_transform_detail',
            ) 
        scale_translate_form.fields['is_translate'].widget = ScaleTranslateCreateWidget(
            create_form=scale_translate_form.formTranslateCreate, 
            name='scales-translate-create', 
            choices=scale_translate_form.PREDEFINDED_TRANSLATE_OPTIONS
            )
        subforms = []
        subforms.append(scale_form)
        subforms.append(scale_translate_form)
        return render(request, 'teacherapp/job_create.html', context={
            'schedule': schedule,
            'control_type': control_type,
            'form': form,
            'subforms': subforms,
        })

    def post(self, request, schedule_id, control_type_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        control_type = get_object_or_404(ControlType, id=control_type_id)
        form = JobForm(
            data=request.POST,
            initial={'control_type': control_type},
            prefix='job_main_form_create',
        )
        scale_form = ControlTypeScale(
            request.POST, 
            data_list=ControlScale.DIMENSION_CHOICES, 
            prefix='control_type_scale_create',
            )
        scale_translate_form = ControlTypeScaleTranslate(
            data=request.POST,
            prefix='control_type_scale_transform_detail',
            ) 
        if form.is_valid() and scale_form.is_valid():
            if scale_translate_form.is_valid():
                if scale_translate_form.cleaned_data['is_translate']==ControlTypeScaleTranslate.FROM_N_TO_FIVE:
                    translate_form = ScaleTranslateCreate(request.POST, prefix="ScaleTranslateCreate")
                    if translate_form.is_valid():
                        translate_object = translate_form.save()
                        scale_instance = scale_form.instance
                        scale_instance.to_five = translate_object
                        scale_form.instance = scale_instance
            else:
                scale_translate_form = ControlTypeScaleTranslate(
                    prefix='control_type_scale_transform_detail',
                    )
            scale_object = scale_form.save()
            model_instance = form.instance
            model_instance.scale = scale_object
            form.instance = model_instance
            new_obj = form.save()
            messages.success(request, 'Новая работа создана!')
            UpdateJobGrades(schedule)
            return redirect(new_obj)
        subforms = []
        subforms.append(scale_form)
        subforms.append(scale_translate_form)
        return render(request, 'teacherapp/job_create.html', context={
            'schedule': schedule,
            'control_type': control_type,
            'form': form,
            'subforms': subforms,
        })
        

class Control_type_job_detail(LoginJobMixin, View):
    def get(self, request, schedule_id, control_type_id, job_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        control_type = get_object_or_404(ControlType, id=control_type_id)
        job = get_object_or_404(ControlWork, id=job_id)
        control_scale = get_object_or_404(ControlScale, control_work=job)
        control_scale_translate = ControlScaleTranslate.objects.filter(control_scale=control_scale).first() # object or null

        form = JobForm(
            instance=job,
            prefix='job_main_form_detail',
        )
        scale_form = ControlTypeScale(
            instance=control_scale,
            data_list=ControlScale.DIMENSION_CHOICES, 
            prefix='control_type_scale_detail',
            )
        if control_scale_translate:
            scale_translate_form = ControlTypeScaleTranslate(
                prefix='control_type_scale_transform_detail',
                initial={'is_translate': ControlTypeScaleTranslate.FROM_N_TO_FIVE},
                use_required_attribute=False,
                )
            scale_translate_form.formTranslateCreate = ScaleTranslateCreate(
                prefix="ScaleTranslate_detail", 
                instance=control_scale_translate,
                use_required_attribute=False
                )
            scale_translate_form.fields['is_translate'].widget = ScaleTranslateCreateWidget(
                create_form=scale_translate_form.formTranslateCreate, 
                name='scales-translate-create', 
                choices=scale_translate_form.PREDEFINDED_TRANSLATE_OPTIONS
                )
        else:
            scale_translate_form = ControlTypeScaleTranslate(
                prefix='control_type_scale_transform_detail',
                use_required_attribute=False,
                )
            scale_translate_form.formTranslateCreate = ScaleTranslateCreate(
                prefix="ScaleTranslate_detail", 
                instance=control_scale_translate,
                )
            scale_translate_form.fields['is_translate'].widget = ScaleTranslateCreateWidget(
                create_form=scale_translate_form.formTranslateCreate, 
                name='scales-translate-create', 
                choices=scale_translate_form.PREDEFINDED_TRANSLATE_OPTIONS
                )
        controlCriterions = job.criterions.all().order_by('criterion_number')
        criterionsweights = {}
        for controlCriterion in controlCriterions:
            criterionsweights[controlCriterion.id]=ControlTypesCriterionWeight(instance=controlCriterion, prefix=controlCriterion.id)
        criterion_list = job.criterions.filter(is_subcriterion=False).order_by('criterion_number')
        subforms = []
        subforms.append(scale_form)
        subforms.append(scale_translate_form)
        return render(request, 'teacherapp/job_detail.html', context={
            'schedule': schedule,
            'control_type': control_type,
            'job': job,
            'form': form,
            'subforms': subforms,
            'criterionsweights': criterionsweights,
            'criterion_list': criterion_list,
        })

    def post(self, request, schedule_id, control_type_id, job_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        control_type = get_object_or_404(ControlType, id=control_type_id)
        job = get_object_or_404(ControlWork, id=job_id)
        control_scale = get_object_or_404(ControlScale, control_work=job)
        control_scale_translate = ControlScaleTranslate.objects.filter(control_scale=control_scale).first() # object or null

        form = JobForm(
            data=request.POST,
            instance=job,
            prefix='job_main_form_detail',
        )
        scale_form = ControlTypeScale(
            data=request.POST,
            instance=control_scale,
            data_list=ControlScale.DIMENSION_CHOICES, 
            prefix='control_type_scale_detail',
            )
        scale_translate_form = ControlTypeScaleTranslate(
            request.POST,
            prefix='control_type_scale_transform_detail',
            use_required_attribute=False,
            )
        scale_translate_form.formTranslateCreate = ScaleTranslateCreate(
            request.POST,
            prefix="ScaleTranslate_detail", 
            instance=control_scale_translate,
            use_required_attribute=False,
            )
        scale_translate_form.fields['is_translate'].widget = ScaleTranslateCreateWidget(
            create_form=scale_translate_form.formTranslateCreate, 
            name='scales-translate-create', 
            choices=scale_translate_form.PREDEFINDED_TRANSLATE_OPTIONS
            ) 
        # save start
        if form.is_valid() and scale_form.is_valid():
            if scale_translate_form.is_valid():
                if scale_translate_form.cleaned_data['is_translate']==ControlTypeScaleTranslate.FROM_N_TO_FIVE:
                    if scale_translate_form.formTranslateCreate.is_valid():
                        translate_object = scale_translate_form.formTranslateCreate.save()
                        scale_instance = scale_form.instance
                        scale_instance.to_five = translate_object
                        scale_form.instance = scale_instance  
            else:
                scale_translate_form = ControlTypeScaleTranslate(
                    prefix='control_type_scale_transform_detail',
                    use_required_attribute=False,
                    )
                scale_translate_form.formTranslateCreate = ScaleTranslateCreate(
                    data=request.POST,
                    prefix="ScaleTranslate_detail", 
                    use_required_attribute=False,
                    )
                if control_scale_translate:
                    control_scale_translate.delete()
                    scale_instance = scale_form.instance
                    scale_instance.to_five = None
                    scale_form.instance = scale_instance  
            scale_object = scale_form.save()
            model_instance = form.instance
            model_instance.scale = scale_object
            form.instance = model_instance
            new_obj = form.save()
            messages.success(request, 'Информация о работе успешно изменена!') 
        # save end
        subforms = []
        subforms.append(scale_form)
        subforms.append(scale_translate_form)
            
        controlCriterions = job.criterions.all().order_by('criterion_number')
        criterionsweights = {}
        for controlCriterion in controlCriterions:
            criterionsweights[controlCriterion.id]=ControlTypesCriterionWeight(instance=controlCriterion, prefix=controlCriterion.id)
        criterion_list = job.criterions.filter(is_subcriterion=False).order_by('criterion_number')
        return render(request, 'teacherapp/job_detail.html', context={
            'schedule': schedule,
            'control_type': control_type,
            'job': job,
            'form': form,
            'subforms': subforms,
            'criterionsweights': criterionsweights,
            'criterion_list': criterion_list,
        })


class Control_type_job_delete(LoginJobMixin, View):
    def post(self, request, schedule_id, control_type_id, job_id):
        control_type = get_object_or_404(ControlType, id=control_type_id)
        job = get_object_or_404(ControlWork, id=job_id)
        job.delete()
        messages.success(request, 'Работа успешно удалена!')
        return redirect(control_type.get_absolute_url())


class Control_type_criterion_list(LoginJobMixin, View):
    def get(self, request, schedule_id, control_type_id, job_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        control_type = get_object_or_404(ControlType, id=control_type_id)
        job = get_object_or_404(ControlWork, id=job_id)
        controlCriterions = job.criterions.all().order_by('criterion_number')
        criterionsweights = {}
        for controlCriterion in controlCriterions:
            criterionsweights[controlCriterion.id]=ControlTypesCriterionWeight(instance=controlCriterion, prefix=controlCriterion.id)
        criterion_list = job.criterions.filter(is_subcriterion=False).order_by('criterion_number')
        return render(request, 'teacherapp/criterion_list.html', context={
            'schedule': schedule,
            'control_type': control_type,
            'job': job,
            'criterionsweights': criterionsweights,
            'criterion_list': criterion_list,
        })

    def post(self, request, schedule_id, control_type_id, job_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        control_type = get_object_or_404(ControlType, id=control_type_id)
        job = get_object_or_404(ControlWork, id=job_id)

        controlCriterions = job.criterions.all().order_by('criterion_number')
        is_success = True
        criterionsweights = {}
        for controlCriterion in controlCriterions:
            criterion_form = ControlTypesCriterionWeight(
                data=request.POST,
                instance=controlCriterion,
                prefix=controlCriterion.id
                )
            if criterion_form.is_valid():
                criterion_form.save()
            else:
                is_success = False
            criterionsweights[controlCriterion.id] = criterion_form
        if is_success:
            messages.success(request, 'Информация о всех критериях обновлена!')
        criterion_list = job.criterions.filter(is_subcriterion=False).order_by('criterion_number')
        return render(request, 'teacherapp/criterion_list.html', context={
            'schedule': schedule,
            'control_type': control_type,
            'job': job,
            'criterionsweights': criterionsweights,
            'criterion_list': criterion_list,
        })


class Control_type_criterion_create(LoginJobMixin, View):
    def get(self, request, schedule_id, control_type_id, job_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        control_type = get_object_or_404(ControlType, id=control_type_id)
        job = get_object_or_404(ControlWork, id=job_id)
        initial_criterion_number = ControlCriterion.objects.filter(control_works=job).aggregate(Max('criterion_number'))
        initial_criterion_number = initial_criterion_number['criterion_number__max']
        if not initial_criterion_number:
            initial_criterion_number = 0
        initial_criterion_number += 1
        form = CriterionForm(
            prefix="criterion_create",
            initial={'criterion_number': initial_criterion_number},
            )
        # form_scale = 
        scale_form = ControlTypeScale(
            data_list=ControlScale.DIMENSION_CHOICES, 
            prefix='control_type_scale_create',
            )
        scale_translate_form = ControlTypeScaleTranslate(
            prefix='control_type_scale_transform_detail',
            ) 
        scale_translate_form.fields['is_translate'].widget = ScaleTranslateCreateWidget(
            create_form=scale_translate_form.formTranslateCreate, 
            name='scales-translate-create', 
            choices=scale_translate_form.PREDEFINDED_TRANSLATE_OPTIONS
            )
        subforms = []
        subforms.append(scale_form)
        #subforms.append(scale_translate_form)
        all_weights = job.criterions.filter(is_subcriterion=False).aggregate(Sum('weight'))
        return render(request, 'teacherapp/criterion_create.html', context={
            'schedule': schedule,
            'control_type': control_type,
            'job': job,
            'form': form,
            'subforms': subforms,
            'all_weights': all_weights,
        })

    def post(self, request, schedule_id, control_type_id, job_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        control_type = get_object_or_404(ControlType, id=control_type_id)
        job = get_object_or_404(ControlWork, id=job_id)
        form = CriterionForm(
            data=request.POST,
            prefix="criterion_create",
            )
        scale_form = ControlTypeScale(
            request.POST, 
            data_list=ControlScale.DIMENSION_CHOICES, 
            prefix='control_type_scale_create',
            )
        scale_translate_form = ControlTypeScaleTranslate(
            data=request.POST,
            prefix='control_type_scale_transform_detail',
            ) 
        if form.is_valid():
            if scale_form.is_valid():
                if scale_translate_form.is_valid():
                    if scale_translate_form.cleaned_data['is_translate']==ControlTypeScaleTranslate.FROM_N_TO_FIVE:
                        translate_form = ScaleTranslateCreate(request.POST, prefix="ScaleTranslateCreate")
                        if translate_form.is_valid():
                            translate_object = translate_form.save()
                            scale_instance = scale_form.instance
                            scale_instance.to_five = translate_object
                            scale_form.instance = scale_instance
                else:
                    scale_translate_form = ControlTypeScaleTranslate(
                        prefix='control_type_scale_transform_detail',
                        ) 
                scale_object = scale_form.save()
                model_instance = form.instance
                model_instance.scale = scale_object
                form.instance = model_instance
                new_form = form.save()
                job.criterions.add(new_form)
                messages.success(request, 'Новый критерий создан!')
                return redirect(new_form)  
        subforms = []
        subforms.append(scale_form)
        #subforms.append(scale_translate_form)
        all_weights = job.criterions.filter(is_subcriterion=False).aggregate(Sum('weight'))
        return render(request, 'teacherapp/criterion_create.html', context={
            'schedule': schedule,
            'control_type': control_type,
            'job': job,
            'form': form,
            'subforms': subforms,
            'all_weights': all_weights,
        })


class Control_type_criterion_detail(LoginCriterionMixin, View):
    def get(self, request, schedule_id, control_type_id, job_id, criterion_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        control_type = get_object_or_404(ControlType, id=control_type_id)
        job = get_object_or_404(ControlWork, id=job_id)
        criterion = get_object_or_404(ControlCriterion, id=criterion_id)

        control_scale = get_object_or_404(ControlScale, criterion=criterion)
        control_scale_translate = ControlScaleTranslate.objects.filter(control_scale=control_scale).first() # object or null

        form = CriterionForm(
            instance=criterion,
            prefix="criterion_detail",
            )
        scale_form = ControlTypeScale(
            instance=control_scale,
            data_list=ControlScale.DIMENSION_CHOICES, 
            prefix='control_type_scale_detail',
            )
        if control_scale_translate:
            scale_translate_form = ControlTypeScaleTranslate(
                prefix='control_type_scale_transform_detail',
                initial={'is_translate': ControlTypeScaleTranslate.FROM_N_TO_FIVE},
                use_required_attribute=False,
                )
            scale_translate_form.formTranslateCreate = ScaleTranslateCreate(
                prefix="ScaleTranslate_detail", 
                instance=control_scale_translate,
                use_required_attribute=False
                )
            scale_translate_form.fields['is_translate'].widget = ScaleTranslateCreateWidget(
                create_form=scale_translate_form.formTranslateCreate, 
                name='scales-translate-create', 
                choices=scale_translate_form.PREDEFINDED_TRANSLATE_OPTIONS
                )
        else:
            scale_translate_form = ControlTypeScaleTranslate(
                prefix='control_type_scale_transform_detail',
                use_required_attribute=False,
                )
            scale_translate_form.formTranslateCreate = ScaleTranslateCreate(
                prefix="ScaleTranslate_detail", 
                instance=control_scale_translate,
                )
            scale_translate_form.fields['is_translate'].widget = ScaleTranslateCreateWidget(
                create_form=scale_translate_form.formTranslateCreate, 
                name='scales-translate-create', 
                choices=scale_translate_form.PREDEFINDED_TRANSLATE_OPTIONS
                )
        subforms = []
        subforms.append(scale_form)
        #subforms.append(scale_translate_form)
        if criterion.is_subcriterion:
            all_weights = criterion.subcriterion.all().first().subcriterion.all().aggregate(Sum('weight'))
        else:
            all_weights = job.criterions.filter(is_subcriterion=False).aggregate(Sum('weight'))
        all_weights['weight__sum'] -= criterion.weight

        return render(request, 'teacherapp/criterion_detail.html', context={
            'schedule': schedule,
            'control_type': control_type,
            'job': job,
            'criterion': criterion,
            'form': form,
            'subforms': subforms,
            'all_weights': all_weights,
            })

    def post(self, request, schedule_id, control_type_id, job_id, criterion_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        control_type = get_object_or_404(ControlType, id=control_type_id)
        job = get_object_or_404(ControlWork, id=job_id)
        criterion = get_object_or_404(ControlCriterion, id=criterion_id)
        control_scale = get_object_or_404(ControlScale, criterion=criterion)
        control_scale_translate = ControlScaleTranslate.objects.filter(control_scale=control_scale).first() # object or null
        form = CriterionForm(
            data=request.POST,
            instance=criterion,
            prefix="criterion_detail",
            )
        scale_form = ControlTypeScale(
            data=request.POST,
            instance=control_scale,
            data_list=ControlScale.DIMENSION_CHOICES, 
            prefix='control_type_scale_detail',
            )
        scale_translate_form = ControlTypeScaleTranslate(
            request.POST,
            prefix='control_type_scale_transform_detail',
            use_required_attribute=False,
            )
        scale_translate_form.formTranslateCreate = ScaleTranslateCreate(
            request.POST,
            prefix="ScaleTranslate_detail", 
            instance=control_scale_translate,
            use_required_attribute=False,
            )
        scale_translate_form.fields['is_translate'].widget = ScaleTranslateCreateWidget(
            create_form=scale_translate_form.formTranslateCreate, 
            name='scales-translate-create', 
            choices=scale_translate_form.PREDEFINDED_TRANSLATE_OPTIONS
            ) 
        # save start
        if form.is_valid() and scale_form.is_valid():
            if scale_translate_form.is_valid():
                if scale_translate_form.cleaned_data['is_translate']==ControlTypeScaleTranslate.FROM_N_TO_FIVE:
                    if scale_translate_form.formTranslateCreate.is_valid():
                        translate_object = scale_translate_form.formTranslateCreate.save()
                        scale_instance = scale_form.instance
                        scale_instance.to_five = translate_object
                        scale_form.instance = scale_instance  
            else:
                scale_translate_form = ControlTypeScaleTranslate(
                    prefix='control_type_scale_transform_detail',
                    use_required_attribute=False,
                    )
                scale_translate_form.formTranslateCreate = ScaleTranslateCreate(
                    data=request.POST,
                    prefix="ScaleTranslate_detail", 
                    use_required_attribute=False,
                    )
                if control_scale_translate:
                    control_scale_translate.delete()
                    scale_instance = scale_form.instance
                    scale_instance.to_five = None
                    scale_form.instance = scale_instance  
            scale_object = scale_form.save()
            model_instance = form.instance
            model_instance.scale = scale_object
            form.instance = model_instance
            new_form = form.save()
            messages.success(request, 'Информация о критерии обновлена!') 
        # save end
        subforms = []
        subforms.append(scale_form)
        #subforms.append(scale_translate_form)
        if criterion.is_subcriterion:
            all_weights = criterion.subcriterion.all().first().subcriterion.all().aggregate(Sum('weight'))
        else:
            all_weights = job.criterions.filter(is_subcriterion=False).aggregate(Sum('weight'))
        all_weights['weight__sum'] -= criterion.weight
        return render(request, 'teacherapp/criterion_detail.html', context={
            'schedule': schedule,
            'control_type': control_type,
            'job': job,
            'criterion': criterion,
            'form': form,
            'subforms': subforms,
            'all_weights': all_weights,
            })


class Control_type_criterion_delete(LoginCriterionMixin, View):
    def post(self, request, schedule_id, control_type_id, job_id, criterion_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        control_type = get_object_or_404(ControlType, id=control_type_id)
        job = get_object_or_404(ControlWork, id=job_id)
        criterion = get_object_or_404(ControlCriterion, id=criterion_id)
        criterion.delete()
        messages.success(request, 'Критерий успешно удален!')
        return redirect(reverse("teacherapp_control_type_criterion_list_url", kwargs={
            "schedule_id": schedule.id, 
            'control_type_id': control_type.id,
            'job_id': job.id,
            }))


class Control_type_subcriterion_create(LoginCriterionMixin, View):
    def get(self, request, schedule_id, control_type_id, job_id, criterion_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        control_type = get_object_or_404(ControlType, id=control_type_id)
        job = get_object_or_404(ControlWork, id=job_id)
        criterion = get_object_or_404(ControlCriterion, id=criterion_id)
        initial_criterion_number = ControlCriterion.objects.filter(subcriterion=criterion).aggregate(Max('criterion_number'))
        initial_criterion_number = initial_criterion_number['criterion_number__max']
        if not initial_criterion_number:
            initial_criterion_number = 0
        initial_criterion_number += 1
        form = CriterionForm(
            prefix="criterion_create",
            initial={'criterion_number': initial_criterion_number},
            )
        scale_form = ControlTypeScale(
            data_list=ControlScale.DIMENSION_CHOICES, 
            prefix='control_type_scale_create',
            )
        scale_translate_form = ControlTypeScaleTranslate(
            prefix='control_type_scale_transform_detail',
            ) 
        scale_translate_form.fields['is_translate'].widget = ScaleTranslateCreateWidget(
            create_form=scale_translate_form.formTranslateCreate, 
            name='scales-translate-create', 
            choices=scale_translate_form.PREDEFINDED_TRANSLATE_OPTIONS
            )
        subforms = []
        subforms.append(scale_form)
        #subforms.append(scale_translate_form)
        all_weights = criterion.subcriterion.all().aggregate(Sum('weight'))
        return render(request, 'teacherapp/subcriterion_create.html', context={
            'schedule': schedule,
            'control_type': control_type,
            'job': job,
            'criterion': criterion,
            'form': form,
            'subforms': subforms,
            'all_weights': all_weights,
        })
    
    def post(self, request, schedule_id, control_type_id, job_id, criterion_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        control_type = get_object_or_404(ControlType, id=control_type_id)
        job = get_object_or_404(ControlWork, id=job_id)
        criterion = get_object_or_404(ControlCriterion, id=criterion_id)
        form = CriterionForm(
            data=request.POST,
            prefix="criterion_create",
            )
        scale_form = ControlTypeScale(
            request.POST, 
            data_list=ControlScale.DIMENSION_CHOICES, 
            prefix='control_type_scale_create',
            )
        scale_translate_form = ControlTypeScaleTranslate(
            data=request.POST,
            prefix='control_type_scale_transform_detail',
            ) 
        if form.is_valid():
            if scale_form.is_valid():
                if scale_translate_form.is_valid():
                    if scale_translate_form.cleaned_data['is_translate']==ControlTypeScaleTranslate.FROM_N_TO_FIVE:
                        translate_form = ScaleTranslateCreate(request.POST, prefix="ScaleTranslateCreate")
                        if translate_form.is_valid():
                            translate_object = translate_form.save()
                            scale_instance = scale_form.instance
                            scale_instance.to_five = translate_object
                            scale_form.instance = scale_instance
                else:
                    scale_translate_form = ControlTypeScaleTranslate(
                        prefix='control_type_scale_transform_detail',
                        ) 
                scale_object = scale_form.save()
                model_instance = form.instance
                model_instance.scale = scale_object
                model_instance.is_subcriterion = True
                form.instance = model_instance
                new_form = form.save()
                criterion.subcriterion.add(new_form)
                job.criterions.add(new_form)
                messages.success(request, 'Новый подкритерий создан!')
                return redirect(new_form)  
        subforms = []
        subforms.append(scale_form)
        #subforms.append(scale_translate_form)
        all_weights = criterion.subcriterion.all().aggregate(Sum('weight'))
        return render(request, 'teacherapp/subcriterion_create.html', context={
            'schedule': schedule,
            'control_type': control_type,
            'job': job,
            'criterion': criterion,
            'form': form,
            'subforms': subforms,
            'all_weights': all_weights,
        })


class Control_type_general_criterion_list(LoginControlTypeMixin, View):
    def get(self, request, schedule_id, control_type_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        control_type = get_object_or_404(ControlType, id=control_type_id)
        controlCriterions = control_type.criterions.all().order_by('criterion_number')
        criterionsweights = {}
        for controlCriterion in controlCriterions:
            criterionsweights[controlCriterion.id]=ControlTypesCriterionWeight(instance=controlCriterion, prefix=controlCriterion.id)
        criterion_list = control_type.criterions.filter(is_subcriterion=False).order_by('criterion_number')
        return render(request, 'teacherapp/general_criterion_list.html', context={
            'schedule': schedule,
            'control_type': control_type,
            'criterionsweights': criterionsweights,
            'criterion_list': criterion_list,
        })

    def post(self, request, schedule_id, control_type_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        control_type = get_object_or_404(ControlType, id=control_type_id)

        controlCriterions = control_type.criterions.all().order_by('criterion_number')
        is_success = True
        criterionsweights = {}
        for controlCriterion in controlCriterions:
            criterion_form = ControlTypesCriterionWeight(
                data=request.POST,
                instance=controlCriterion,
                prefix=controlCriterion.id
                )
            if criterion_form.is_valid():
                criterion_form.save()
            else:
                is_success = False
            criterionsweights[controlCriterion.id] = criterion_form
        if is_success:
            messages.success(request, 'Информация о всех критериях обновлена!')
        criterion_list = control_type.criterions.filter(is_subcriterion=False).order_by('criterion_number')
        return render(request, 'teacherapp/general_criterion_list.html', context={
            'schedule': schedule,
            'control_type': control_type,
            'criterionsweights': criterionsweights,
            'criterion_list': criterion_list,
        })
        

class Control_type_general_criterion_create(LoginControlTypeMixin, View):
    def get(self, request, schedule_id, control_type_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        control_type = get_object_or_404(ControlType, id=control_type_id)
        initial_criterion_number = ControlCriterion.objects.filter(control_type=control_type).aggregate(Max('criterion_number'))
        initial_criterion_number = initial_criterion_number['criterion_number__max']
        if not initial_criterion_number:
            initial_criterion_number = 0
        initial_criterion_number += 1
        form = CriterionForm(
            prefix="criterion_create",
            initial={'criterion_number': initial_criterion_number},
            )
        # form_scale = 
        scale_form = ControlTypeScale(
            data_list=ControlScale.DIMENSION_CHOICES, 
            prefix='control_type_scale_create',
            )
        scale_translate_form = ControlTypeScaleTranslate(
            prefix='control_type_scale_transform_detail',
            ) 
        scale_translate_form.fields['is_translate'].widget = ScaleTranslateCreateWidget(
            create_form=scale_translate_form.formTranslateCreate, 
            name='scales-translate-create', 
            choices=scale_translate_form.PREDEFINDED_TRANSLATE_OPTIONS
            )
        subforms = []
        subforms.append(scale_form)
        #subforms.append(scale_translate_form)
        all_weights = control_type.criterions.filter(is_subcriterion=False).aggregate(Sum('weight'))
        return render(request, 'teacherapp/general_criterion_create.html', context={
            'schedule': schedule,
            'control_type': control_type,
            'form': form,
            'subforms': subforms,
            'all_weights': all_weights,
        })
        
    def post(self, request, schedule_id, control_type_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        control_type = get_object_or_404(ControlType, id=control_type_id)
        form = CriterionForm(
            data=request.POST,
            prefix="criterion_create",
            )
        scale_form = ControlTypeScale(
            request.POST, 
            data_list=ControlScale.DIMENSION_CHOICES, 
            prefix='control_type_scale_create',
            )
        scale_translate_form = ControlTypeScaleTranslate(
            data=request.POST,
            prefix='control_type_scale_transform_detail',
            ) 
        if form.is_valid():
            if scale_form.is_valid():
                if scale_translate_form.is_valid():
                    if scale_translate_form.cleaned_data['is_translate']==ControlTypeScaleTranslate.FROM_N_TO_FIVE:
                        translate_form = ScaleTranslateCreate(request.POST, prefix="ScaleTranslateCreate")
                        if translate_form.is_valid():
                            translate_object = translate_form.save()
                            scale_instance = scale_form.instance
                            scale_instance.to_five = translate_object
                            scale_form.instance = scale_instance
                else:
                    scale_translate_form = ControlTypeScaleTranslate(
                        prefix='control_type_scale_transform_detail',
                        ) 
                scale_object = scale_form.save()
                model_instance = form.instance
                model_instance.scale = scale_object
                form.instance = model_instance
                new_form = form.save()
                control_type.criterions.add(new_form)
                messages.success(request, 'Новый критерий создан!')
                return redirect(reverse("teacherapp_control_type_general_criterion_detail_url", kwargs={
                    'schedule_id': schedule.id,
                    'control_type_id': control_type.id,
                    'criterion_id': new_form.id,
                }))
        subforms = []
        subforms.append(scale_form)
        #subforms.append(scale_translate_form)
        all_weights = control_type.criterions.filter(is_subcriterion=False).aggregate(Sum('weight'))
        return render(request, 'teacherapp/general_criterion_create.html', context={
            'schedule': schedule,
            'control_type': control_type,
            'form': form,
            'subforms': subforms,
            'all_weights': all_weights,
        })


class Control_type_general_criterion_detail(LoginGeneralCriterionMixin, View):
    def get(self, request, schedule_id, control_type_id, criterion_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        control_type = get_object_or_404(ControlType, id=control_type_id)
        criterion = get_object_or_404(ControlCriterion, id=criterion_id)
        control_scale = get_object_or_404(ControlScale, criterion=criterion)
        control_scale_translate = ControlScaleTranslate.objects.filter(control_scale=control_scale).first() # object or null
        form = CriterionForm(
            instance=criterion,
            prefix="criterion_detail",
            )
        scale_form = ControlTypeScale(
            instance=control_scale,
            data_list=ControlScale.DIMENSION_CHOICES, 
            prefix='control_type_scale_detail',
            )
        if control_scale_translate:
            scale_translate_form = ControlTypeScaleTranslate(
                prefix='control_type_scale_transform_detail',
                initial={'is_translate': ControlTypeScaleTranslate.FROM_N_TO_FIVE},
                use_required_attribute=False,
                )
            scale_translate_form.formTranslateCreate = ScaleTranslateCreate(
                prefix="ScaleTranslate_detail", 
                instance=control_scale_translate,
                use_required_attribute=False
                )
            scale_translate_form.fields['is_translate'].widget = ScaleTranslateCreateWidget(
                create_form=scale_translate_form.formTranslateCreate, 
                name='scales-translate-create', 
                choices=scale_translate_form.PREDEFINDED_TRANSLATE_OPTIONS
                )
        else:
            scale_translate_form = ControlTypeScaleTranslate(
                prefix='control_type_scale_transform_detail',
                use_required_attribute=False,
                )
            scale_translate_form.formTranslateCreate = ScaleTranslateCreate(
                prefix="ScaleTranslate_detail", 
                instance=control_scale_translate,
                )
            scale_translate_form.fields['is_translate'].widget = ScaleTranslateCreateWidget(
                create_form=scale_translate_form.formTranslateCreate, 
                name='scales-translate-create', 
                choices=scale_translate_form.PREDEFINDED_TRANSLATE_OPTIONS
                )
        subforms = []
        subforms.append(scale_form)
        #subforms.append(scale_translate_form)
        if criterion.is_subcriterion:
            all_weights = criterion.subcriterion.all().first().subcriterion.all().aggregate(Sum('weight'))
        else:
            all_weights = control_type.criterions.filter(is_subcriterion=False).aggregate(Sum('weight'))
        all_weights['weight__sum'] -= criterion.weight
        return render(request, 'teacherapp/general_criterion_detail.html', context={
            'schedule': schedule,
            'control_type': control_type,
            'criterion': criterion,
            'form': form,
            'subforms': subforms,
            'all_weights': all_weights,
            })

    def post(self, request, schedule_id, control_type_id, criterion_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        control_type = get_object_or_404(ControlType, id=control_type_id)
        criterion = get_object_or_404(ControlCriterion, id=criterion_id)
        control_scale = get_object_or_404(ControlScale, criterion=criterion)
        control_scale_translate = ControlScaleTranslate.objects.filter(control_scale=control_scale).first() # object or null
        form = CriterionForm(
            data=request.POST,
            instance=criterion,
            prefix="criterion_detail",
            )
        scale_form = ControlTypeScale(
            data=request.POST,
            instance=control_scale,
            data_list=ControlScale.DIMENSION_CHOICES, 
            prefix='control_type_scale_detail',
            )
        scale_translate_form = ControlTypeScaleTranslate(
            request.POST,
            prefix='control_type_scale_transform_detail',
            use_required_attribute=False,
            )
        scale_translate_form.formTranslateCreate = ScaleTranslateCreate(
            request.POST,
            prefix="ScaleTranslate_detail", 
            instance=control_scale_translate,
            use_required_attribute=False,
            )
        scale_translate_form.fields['is_translate'].widget = ScaleTranslateCreateWidget(
            create_form=scale_translate_form.formTranslateCreate, 
            name='scales-translate-create', 
            choices=scale_translate_form.PREDEFINDED_TRANSLATE_OPTIONS
            ) 
        # save start
        if form.is_valid() and scale_form.is_valid():
            if scale_translate_form.is_valid():
                if scale_translate_form.cleaned_data['is_translate']==ControlTypeScaleTranslate.FROM_N_TO_FIVE:
                    if scale_translate_form.formTranslateCreate.is_valid():
                        translate_object = scale_translate_form.formTranslateCreate.save()
                        scale_instance = scale_form.instance
                        scale_instance.to_five = translate_object
                        scale_form.instance = scale_instance  
            else:
                scale_translate_form = ControlTypeScaleTranslate(
                    prefix='control_type_scale_transform_detail',
                    use_required_attribute=False,
                    )
                scale_translate_form.formTranslateCreate = ScaleTranslateCreate(
                    data=request.POST,
                    prefix="ScaleTranslate_detail", 
                    use_required_attribute=False,
                    )
                if control_scale_translate:
                    control_scale_translate.delete()
                    scale_instance = scale_form.instance
                    scale_instance.to_five = None
                    scale_form.instance = scale_instance  
            scale_object = scale_form.save()
            model_instance = form.instance
            model_instance.scale = scale_object
            form.instance = model_instance
            new_form = form.save()
            messages.success(request, 'Информация о критерии обновлена!') 
        # save end
        subforms = []
        subforms.append(scale_form)
        #subforms.append(scale_translate_form)
        if criterion.is_subcriterion:
            all_weights = criterion.subcriterion.all().first().subcriterion.all().aggregate(Sum('weight'))
        else:
            all_weights = control_type.criterions.filter(is_subcriterion=False).aggregate(Sum('weight'))
        all_weights['weight__sum'] -= criterion.weight
        return render(request, 'teacherapp/general_criterion_detail.html', context={
            'schedule': schedule,
            'control_type': control_type,
            'criterion': criterion,
            'form': form,
            'subforms': subforms,
            'all_weights': all_weights,
            })


class Control_type_general_criterion_delete(LoginGeneralCriterionMixin, View):
    def post(self, request, schedule_id, control_type_id, criterion_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        control_type = get_object_or_404(ControlType, id=control_type_id)
        criterion = get_object_or_404(ControlCriterion, id=criterion_id)
        criterion.delete()
        messages.success(request, 'Критерий успешно удален!')
        return redirect(reverse("teacherapp_control_type_general_criterion_list_url", kwargs={
            "schedule_id": schedule.id, 
            'control_type_id': control_type.id,
            }))


class Control_type_general_criterion_create_subcriterion(LoginGeneralCriterionMixin, View):
    def get(self, request, schedule_id, control_type_id, criterion_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        control_type = get_object_or_404(ControlType, id=control_type_id)
        criterion = get_object_or_404(ControlCriterion, id=criterion_id)
        initial_criterion_number = ControlCriterion.objects.filter(subcriterion=criterion).aggregate(Max('criterion_number'))
        initial_criterion_number = initial_criterion_number['criterion_number__max']
        if not initial_criterion_number:
            initial_criterion_number = 0
        initial_criterion_number += 1
        form = CriterionForm(
            prefix="criterion_create",
            initial={'criterion_number': initial_criterion_number},
            )
        scale_form = ControlTypeScale(
            data_list=ControlScale.DIMENSION_CHOICES, 
            prefix='control_type_scale_create',
            )
        scale_translate_form = ControlTypeScaleTranslate(
            prefix='control_type_scale_transform_detail',
            ) 
        scale_translate_form.fields['is_translate'].widget = ScaleTranslateCreateWidget(
            create_form=scale_translate_form.formTranslateCreate, 
            name='scales-translate-create', 
            choices=scale_translate_form.PREDEFINDED_TRANSLATE_OPTIONS
            )
        subforms = []
        subforms.append(scale_form)
        #subforms.append(scale_translate_form)
        all_weights = criterion.subcriterion.all().aggregate(Sum('weight'))
        return render(request, 'teacherapp/general_criterion_create_subcriterion.html', context={
            'schedule': schedule,
            'control_type': control_type,
            'criterion': criterion,
            'form': form,
            'subforms': subforms,
            'all_weights': all_weights,
        })
    
    def post(self, request, schedule_id, control_type_id, criterion_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        control_type = get_object_or_404(ControlType, id=control_type_id)
        criterion = get_object_or_404(ControlCriterion, id=criterion_id)
        form = CriterionForm(
            data=request.POST,
            prefix="criterion_create",
            )
        scale_form = ControlTypeScale(
            request.POST, 
            data_list=ControlScale.DIMENSION_CHOICES, 
            prefix='control_type_scale_create',
            )
        scale_translate_form = ControlTypeScaleTranslate(
            data=request.POST,
            prefix='control_type_scale_transform_detail',
            ) 
        if form.is_valid():
            if scale_form.is_valid():
                if scale_translate_form.is_valid():
                    if scale_translate_form.cleaned_data['is_translate']==ControlTypeScaleTranslate.FROM_N_TO_FIVE:
                        translate_form = ScaleTranslateCreate(request.POST, prefix="ScaleTranslateCreate")
                        if translate_form.is_valid():
                            translate_object = translate_form.save()
                            scale_instance = scale_form.instance
                            scale_instance.to_five = translate_object
                            scale_form.instance = scale_instance
                else:
                    scale_translate_form = ControlTypeScaleTranslate(
                        prefix='control_type_scale_transform_detail',
                        ) 
                scale_object = scale_form.save()
                model_instance = form.instance
                model_instance.scale = scale_object
                model_instance.is_subcriterion = True
                form.instance = model_instance
                new_form = form.save()
                criterion.subcriterion.add(new_form)
                control_type.criterions.add(new_form)
                messages.success(request, 'Новый подкритерий создан!')
                return redirect(reverse("teacherapp_control_type_general_criterion_detail_url", kwargs={
                    'schedule_id': schedule.id,
                    'control_type_id': control_type.id,
                    'criterion_id': new_form.id,
                }))
        subforms = []
        subforms.append(scale_form)
        #subforms.append(scale_translate_form)
        all_weights = criterion.subcriterion.all().aggregate(Sum('weight'))
        return render(request, 'teacherapp/subcriterion_create.html', context={
            'schedule': schedule,
            'control_type': control_type,
            'criterion': criterion,
            'form': form,
            'subforms': subforms,
            'all_weights': all_weights,
        })


class Control_type_write_list(LoginControlTypeMixin, View):
    def get(self, request, schedule_id, control_type_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        control_type = get_object_or_404(ControlType, id=control_type_id)
        jobs = control_type.control_works.order_by('work_number')
        return render(request, 'teacherapp/write_job_list.html', context={
            'schedule': schedule,
            'control_type': control_type,
            'jobs': jobs,
        })
                

class Control_type_write_job(LoginJobMixin, View):
    def get(self, request, schedule_id, control_type_id, job_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        control_type = get_object_or_404(ControlType, id=control_type_id)
        job = get_object_or_404(ControlWork, id=job_id)
        control_scale = get_object_or_404(ControlScale, control_work=job)
        bound_forms = []
        points =  control_scale.dimension                                   # какая шкала
        is_radio = True
        for attend in Control_work_grade.objects.filter(controlwork=job).order_by('student__version_in_group'):
            if points==2:
                form = GradeAttendanceFormOffset(instance=attend, prefix=attend.student.id)
            elif points==5:
                form = GradeAttendanceForm(instance=attend, prefix=attend.student.id)
            else:
                form = GradeAttendanceFormNPoint(
                    max_value=attend.controlwork.scale.dimension,
                    instance=attend, 
                    prefix=attend.student.id,
                    )
                is_radio = False
            bound_forms.append(form)
        history_verificaions = TeleWork.objects.filter(Q(control_grade__controlwork=job) & Q(is_checked=True)).order_by('check_date')
        return render(request, 'teacherapp/write_job_detail.html', context={
            'schedule': schedule,
            'control_type': control_type,
            'job': job,
            'grades': bound_forms,
            'is_radio': is_radio,
            'history_verificaions': history_verificaions,
        })

    def post(self, request, schedule_id, control_type_id, job_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        control_type = get_object_or_404(ControlType, id=control_type_id)
        job = get_object_or_404(ControlWork, id=job_id)
        control_scale = get_object_or_404(ControlScale, control_work=job)
        bound_forms = []
        points =  control_scale.dimension                                   # какая шкала
        is_radio = True
        for attend in Control_work_grade.objects.filter(controlwork=job).order_by('student__version_in_group'):
            if points==2:
                bound_form = GradeAttendanceFormOffset(
                    data=request.POST,
                    instance=attend, 
                    prefix=attend.student.id,
                    )
            elif points==5:
                bound_form = GradeAttendanceForm(
                    data=request.POST,
                    instance=attend, 
                    prefix=attend.student.id,
                    )
            else:
                bound_form = GradeAttendanceFormNPoint(
                    data=request.POST,
                    max_value=attend.controlwork.scale.dimension,
                    instance=attend, 
                    prefix=attend.student.id,
                    )
                is_radio = False
            if bound_form.is_valid():
                bound_form.save()
            bound_forms.append(bound_form)
        messages.success(request, 'Информация по оценкам обновлена!')
        history_verificaion = TeleWork.objects.filter(Q(controlwork=job) & Q(is_checked=True)).order_by('check_date').last()
        return render(request, 'teacherapp/write_job_detail.html', context={
            'schedule': schedule,
            'control_type': control_type,
            'job': job,
            'grades': bound_forms,
            'is_radio': is_radio,
            'history_verificaion': history_verificaion,
        })


class Control_type_write_survey_job(LoginJobMixin, View):
    def get(self, request, schedule_id, control_type_id, job_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        control_type = get_object_or_404(ControlType, id=control_type_id)
        job = get_object_or_404(ControlWork, id=job_id)
        control_scale = get_object_or_404(ControlScale, control_work=job)
        bound_forms = []
        points =  control_scale.dimension                                   # какая шкала
        is_radio = True
        for attend in Control_work_grade.objects.filter(controlwork=job).order_by('student__version_in_group'):
            if points==2:
                form = GradeAttendanceFormOffset(instance=attend, prefix=attend.student.id)
            elif points==5:
                form = GradeAttendanceForm(instance=attend, prefix=attend.student.id)
            else:
                form = GradeAttendanceFormNPoint(
                    max_value=attend.controlwork.scale.dimension,
                    instance=attend, 
                    prefix=attend.student.id,
                    )
                is_radio = False
            bound_forms.append(form)
        return render(request, 'teacherapp/job_attendance_survey.html', context={
            'schedule': schedule,
            'control_type': control_type,
            'job': job,
            'grades': bound_forms,
            'is_radio': is_radio,
        })


class WorkVerification(LoginRequiredMixin, View):
    def get(self, request):
        teleworks = TeleWork.objects.filter(
            control_grade__controlwork__control_type__schedule__user__teacher__id=request.user.id,
            is_checked=False,
            ).order_by('delivery_date')
        return render(request, 'teacherapp/work_verification.html', context={
            'teleworks': teleworks,
        })
        #user__teacher__id


class WorkVerificationDetail(VerificationCheckMixin, View):
    def get(self, request, verification_id):
        verification = get_object_or_404(TeleWork, id=verification_id)
        job = get_object_or_404(ControlWork, id=verification.control_grade.controlwork.id)
        criterionsgrades = {}
        last_verification = TeleWork.objects.filter(Q(control_grade=verification.control_grade) &Q(is_checked=True)).last()
        for teleworkCriterion in verification.tele_work_criterions.all():
            controlCriterion = teleworkCriterion.criterion
            points =  controlCriterion.scale.dimension                                   # какая шкала
            is_radio = False
            if points==2:
                form = GradeCriterionFormOffset(
                    instance=teleworkCriterion, 
                    prefix=teleworkCriterion.id,
                    )
            elif points==5:
                if teleworkCriterion.grade == 0:
                    teleworkCriterion.grade = 2
                form = GradeCriterionForm(
                    instance=teleworkCriterion, 
                    prefix=teleworkCriterion.id,
                    )
                is_radio = True
            else:
                form = GradeCriterionFormNPoint(
                    max_value=teleworkCriterion.criterion.scale.dimension,
                    instance=teleworkCriterion, 
                    prefix=teleworkCriterion.id,
                    ) 
            if last_verification:   # если есть предыдущая оцененная работа
                criterion_grade = last_verification.tele_work_criterions.filter(criterion=teleworkCriterion.criterion).first()
                form.initial['grade'] = criterion_grade.grade
            criterionsgrades[teleworkCriterion.id] = form
        iframe_form = TeleWorkCriterionsCommentForm(
            prefix='TeleWorkCriterionsCommentForm',
        ) # comment form
        dimension = job.scale.dimension
        if dimension==2:
            grade_form = TeleWorkGradeFormOffset(
                prefix='TeleWork_grade',
                instance=verification
            )
        elif dimension==5:
            if verification.grade == 0:
                verification.grade = 2
            grade_form = TeleWorkGradeForm(
                prefix='TeleWork_grade',
                instance=verification
            )
        else:
            grade_form = TeleWorkGradeFormNPoint(
                prefix='TeleWork_grade',
                instance=verification
            )
        if last_verification:   # если есть предыдущая оцененная работа
            grade_form.initial['grade'] = last_verification.grade
        return render(request, 'teacherapp/work_verification_detail.html', context={
            'verification': verification,
            'job': job,
            'criterionsgrades': criterionsgrades,
            'iframe_form': iframe_form,
            'grade_form': grade_form,
        })

    def post(self, request, verification_id):
        verification = get_object_or_404(TeleWork, id=verification_id)
        job = get_object_or_404(ControlWork, id=verification.control_grade.controlwork.id)
        criterionsgrades = {}
        for teleworkCriterion in verification.tele_work_criterions.all():
            controlCriterion = teleworkCriterion.criterion
            points =  controlCriterion.scale.dimension                                   # какая шкала
            is_radio = False
            if points==2:
                form = GradeCriterionFormOffset(
                    data=request.POST,
                    instance=teleworkCriterion, 
                    prefix=teleworkCriterion.id,
                    )
            elif points==5:
                if teleworkCriterion.grade == 0:
                    teleworkCriterion.grade = 2
                form = GradeCriterionForm(
                    data=request.POST,
                    instance=teleworkCriterion, 
                    prefix=teleworkCriterion.id,
                    )
                is_radio = True
            else:
                form = GradeCriterionFormNPoint(
                    data=request.POST,
                    max_value=teleworkCriterion.criterion.scale.dimension,
                    instance=teleworkCriterion, 
                    prefix=teleworkCriterion.id,
                    ) 
            criterionsgrades[teleworkCriterion.id] = form
        iframe_form = TeleWorkCriterionsCommentForm(
            prefix='TeleWorkCriterionsCommentForm',
        ) # comment form
        dimension = job.scale.dimension
        if dimension==2:
            grade_form = TeleWorkGradeFormOffset(
                data=request.POST,
                prefix='TeleWork_grade',
                instance=verification
            )
        elif dimension==5:
            if verification.grade == 0:
                verification.grade = 2
            grade_form = TeleWorkGradeForm(
                data=request.POST,
                prefix='TeleWork_grade',
                instance=verification
            )
        else:
            grade_form = TeleWorkGradeFormNPoint(
                data=request.POST,
                prefix='TeleWork_grade',
                instance=verification
            )
        if grade_form.is_valid():
            new_grade = grade_form.save()
            if dimension==2:
                new_grade.grade *= 2
            new_grade.is_checked = True
            new_grade.check_date = time.now()
            # сохранение критериев
            for id, criterionsgrade in criterionsgrades.items():
                if criterionsgrade.is_valid():
                    new_criterion = criterionsgrade.save()
                    if new_criterion.criterion.scale.dimension == 2:
                        new_criterion.grade *= 2
                        new_criterion.save()
            if new_grade.control_grade.grade:
                if new_grade.control_grade.grade<=new_grade.grade:
                    new_grade.control_grade.grade = new_grade.grade
            else:
                new_grade.control_grade.grade = new_grade.grade
            if 'offset' in request.POST:    # если зачет
                new_grade.control_grade.status = Control_work_grade.STATUS_VARIANTS[2][0]
                messages.success(request, 'Работа зачтена!')
            elif 'change' in request.POST:  # если незачет
                new_grade.control_grade.status = Control_work_grade.STATUS_VARIANTS[3][0]
                messages.success(request, 'Работа отправлена на доработку!')
            new_grade.control_grade.save()
            new_grade.save()
            
            return redirect(reverse('teacherapp_works_verification_url'))
            
        return render(request, 'teacherapp/work_verification_detail.html', context={
            'verification': verification,
            'job': job,
            'criterionsgrades': criterionsgrades,
            'iframe_form': iframe_form,
            'grade_form': grade_form,
        }) 


class WorkVerificationAddComment(LoginVerificationMixin, View):
    def post(self, request, verification_id):
        if request.is_ajax():
            input_data = request.POST
            text = input_data['text']
            comment_type = input_data['comment_type']
            teleworkcriterion = input_data['teleworkcriterion']
            teleworkcriterion = get_object_or_404(TeleWorkCriterions, id=teleworkcriterion)
            try:
                comment = TeleWorkCriterionsComment.objects.create(
                    text=text,
                    comment_type=comment_type,
                    teleworkcriterion=teleworkcriterion,
                    )
                return JsonResponse({
                    'success': 'hello there',
                    'text': comment.text,
                    'comment_type': comment.comment_type,
                    'teleworkcriterion': teleworkcriterion.id,
                    'comment_id': comment.id,
                    })
            except Exception as ex:
                print(str(ex))
                return JsonResponse({
                    'error': 'error',
                    })


class WorkVerificationDeleteComment(LoginVerificationMixin, View):
    def post(self, request, verification_id):
        if request.is_ajax():
            input_data = request.POST
            teleworkcomment = input_data['teleworkcomment']
            teleworkcomment = get_object_or_404(TeleWorkCriterionsComment, id=teleworkcomment)
            try:
                teleworkcomment.delete()
                return JsonResponse({
                    'success': 'success',
                    })
            except Exception as ex:
                print(str(ex))
                return JsonResponse({
                    'error': 'error',
                    })


class WorkVerificationHistory(VerificationCheckMixin, View):
    def get(self, request, verification_id):
        verification = get_object_or_404(TeleWork, id=verification_id)
        grade = verification.control_grade
        teleworks = TeleWork.objects.filter(
            control_grade=grade,
            is_checked=True,
            ).order_by('-check_date')
        history_verification = TeleWork.objects.filter(Q(control_grade=grade) & Q(is_checked=True)).order_by('check_date').last()

        criterionsgrades = {}
        for teleworkCriterion in history_verification.tele_work_criterions.all():
            controlCriterion = teleworkCriterion.criterion
            points =  controlCriterion.scale.dimension                                   # какая шкала
            # после студента - добавить
            for student_comment in teleworkCriterion.tele_work_criterion_comment_student.all():
                student_comment.is_checked = True
                student_comment.save()
            if points==2:
                form = GradeCriterionFormOffsetReadonly(
                    instance=teleworkCriterion, 
                    prefix=teleworkCriterion.id,
                    )
            elif points==5:
                if teleworkCriterion.grade == 0:
                    teleworkCriterion.grade = 2
                form = GradeCriterionFormReadonly(
                    instance=teleworkCriterion, 
                    prefix=teleworkCriterion.id,
                    )
            else:
                form = GradeCriterionFormNPointReadonly(
                    max_value=teleworkCriterion.criterion.scale.dimension,
                    instance=teleworkCriterion, 
                    prefix=teleworkCriterion.id,
                    ) 
            criterionsgrades[teleworkCriterion.id] = form
        return render(request, 'teacherapp/verification_history.html', context={
            'verification': verification,
            'teleworks': teleworks,
            'history_verification': history_verification,
            'criterionsgrades': criterionsgrades,
        })


class WorkVerificationHistoryDetail(VerificationUnCheckMixin, View):
    def get(self, request, verification_id, history_verification_id):
        verification = get_object_or_404(TeleWork, id=verification_id)
        history_verification = get_object_or_404(TeleWork, id=history_verification_id)
        grade = verification.control_grade
        criterionsgrades = {}
        for teleworkCriterion in history_verification.tele_work_criterions.all():
            controlCriterion = teleworkCriterion.criterion
            points =  controlCriterion.scale.dimension                                   # какая шкала
            # после студента - добавить
            for student_comment in teleworkCriterion.tele_work_criterion_comment_student.all():
                student_comment.is_checked = True
                student_comment.save()
            if points==2:
                form = GradeCriterionFormOffsetReadonly(
                    instance=teleworkCriterion, 
                    prefix=teleworkCriterion.id,
                    )
            elif points==5:
                if teleworkCriterion.grade == 0:
                    teleworkCriterion.grade = 2
                form = GradeCriterionFormReadonly(
                    instance=teleworkCriterion, 
                    prefix=teleworkCriterion.id,
                    )
            else:
                form = GradeCriterionFormNPointReadonly(
                    max_value=teleworkCriterion.criterion.scale.dimension,
                    instance=teleworkCriterion, 
                    prefix=teleworkCriterion.id,
                    ) 
            criterionsgrades[teleworkCriterion.id] = form
        return render(request, 'teacherapp/verification_history_detail.html', context={
            'verification': verification,
            'history_verification': history_verification,
            'criterionsgrades': criterionsgrades,
        })


class Certification_list(LoginScheduleRequiredMixin, View):
    def get(self, request, schedule_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        certifications = Certification.objects.filter(schedule=schedule).order_by('number')
        return render(request, 'teacherapp/certification_list.html', context={
            'schedule': schedule,
            'certifications': certifications,
        })


class Certification_create(LoginScheduleRequiredMixin, View):
    def get(self, request, schedule_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        certification_num = Certification.objects.filter(schedule=schedule).aggregate(Max('number'))['number__max']
        certification_num = (certification_num if certification_num else 0) + 1
        form = CertificationForm(
            initial={
                'schedule': schedule,
                'number': certification_num,
            },
            prefix='certification_create',
        )
        bool_form = CertificationScaleBoolForm(
            prefix='scaletranslate_create',
        )
        subforms = []
        subforms.append(bool_form)
        job_weights = {}
        for control_type in schedule.control_types.all():
            for control_work in control_type.control_works.all():
                job_form = CertificationJobForm(
                    initial={
                        'control_work': control_work,
                        'weight': control_work.weight,
                    },
                    prefix=control_work.id,
                    use_required_attribute=False,
                )
                job_weights[control_work.id] = job_form
        return render(request, 'teacherapp/certification_create.html', context={
            'schedule': schedule,
            'form': form,
            'subforms': subforms,
            'job_weights': job_weights,
        })

    def post(self, request, schedule_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        form = CertificationForm(
            data=request.POST,
            initial={
                'schedule': schedule,
            },
            prefix='certification_create',
        )
        bool_form = CertificationScaleBoolForm( # scale-translate
            data=request.POST,
            prefix='scaletranslate_create',
        )
        job_weights = {}
        is_success = False
        if form.is_valid():
            new_obj = form.save()
            if bool_form.is_valid():
                if bool_form.cleaned_data['is_translate']==ControlTypeScaleTranslate.FROM_N_TO_FIVE:
                    translate_form = ScaleTranslateCreate(
                        data=request.POST, 
                        prefix="ScaleTranslateCreate",
                        )
                    if translate_form.is_valid():
                        translate_object = translate_form.save()
                        new_obj.scale_translate = translate_object
                        new_obj.save()
            messages.success(request, 'Новая аттестация создана!')
            is_success = True
        for control_type in schedule.control_types.all():
            for control_work in control_type.control_works.all():
                job_form = CertificationJobForm(
                    data=request.POST,
                    prefix=control_work.id,
                    use_required_attribute=False,
                )
                job_instance = job_form.instance
                job_instance.certification = new_obj
                job_form.instance = job_instance
                if job_form.is_valid():
                    job_form.save()
                job_weights[control_work.id] = job_form
        if is_success:
            return redirect(new_obj)  
        subforms = []
        subforms.append(bool_form)
        return render(request, 'teacherapp/certification_create.html', context={
            'schedule': schedule,
            'form': form,
            'subforms': subforms,
            'job_weights': job_weights,
        })


class Certification_detail(CertificationMixin, View):
    def get(self, request, schedule_id, certification_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        certification = get_object_or_404(Certification, id=certification_id)
        form = CertificationForm(
            instance=certification,
            prefix='certification_detail',
        )
        bool_form = CertificationScaleBoolForm(
            prefix='scaletranslate_detail_main',
            use_required_attribute=False,
        )
        translate_form = ScaleTranslateCreate(
            prefix="ScaleTranslate_detail", 
            instance=certification.scale_translate,
            )
        if certification.scale_translate:
            bool_form = CertificationScaleBoolForm(
                prefix='scaletranslate_detail_main',
                initial={'is_translate': ControlTypeScaleTranslate.FROM_N_TO_FIVE},
                use_required_attribute=False,
            )
        job_weights = {}
        for control_type in schedule.control_types.all():
            for control_work in control_type.control_works.all():
                instance = Certification_control_work.objects.filter(Q(certification=certification) & Q(control_work=control_work)).first()
                if instance:
                    job_form = CertificationJobForm(
                        instance=instance,
                        initial={
                            'control_work': control_work,
                            'is_choosed': True,
                        },
                        prefix=control_work.id,
                        use_required_attribute=False,
                    )
                else:
                    job_form = CertificationJobForm(
                        initial={
                            'control_work': control_work,
                            'weight': control_work.weight,
                        },
                        prefix=control_work.id,
                        use_required_attribute=False,
                    )
                job_weights[control_work.id] = job_form
        bool_form.formTranslateCreate = translate_form
        bool_form.fields['is_translate'].widget = ScaleTranslateCreateWidget(
            create_form=bool_form.formTranslateCreate, 
            name='scales-translate-create', 
            choices=bool_form.PREDEFINDED_TRANSLATE_OPTIONS
            )
        subforms = []
        subforms.append(bool_form)
        return render(request, 'teacherapp/certification_detail.html', context={
            'schedule': schedule,
            'certification': certification,
            'form': form,
            'subforms': subforms,
            'job_weights': job_weights,
        })

    def post(self, request, schedule_id, certification_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        certification = get_object_or_404(Certification, id=certification_id)
        form = CertificationForm(
            data=request.POST,
            instance=certification,
            prefix='certification_detail',
        )
        bool_form = CertificationScaleBoolForm(
            data=request.POST,
            prefix='scaletranslate_detail_main',
        )
        translate_form = ScaleTranslateCreate(
            prefix="ScaleTranslate_detail", 
            instance=certification.scale_translate,
            )
        if form.is_valid():
            if bool_form.is_valid():
                if bool_form.cleaned_data['is_translate']==ControlTypeScaleTranslate.FROM_N_TO_FIVE:
                    translate_form = ScaleTranslateCreate(
                        data=request.POST,
                        prefix="ScaleTranslate_detail", 
                        instance=certification.scale_translate,
                        )
                    if translate_form.is_valid():
                        translate_object = translate_form.save()    # сохранение переводчика шкалы
                        form_instance = form.instance
                        form_instance.scale_translate = translate_object
                        form.instance = form_instance
            else:   # если не надо создавать/изменять переводчик, то удалить старый
                bool_form = CertificationScaleBoolForm(
                    prefix='scaletranslate_detail_main',
                )
                if certification.scale_translate:
                    certification.scale_translate.delete()
                    form_instance = form.instance
                    form_instance.scale_translate = None
                    form.instance = form_instance
            form.save() # сохранение аттестации
            messages.success(request, 'Аттестация успешно изменена!')
        job_weights = {}
        for control_type in schedule.control_types.all():
            for control_work in control_type.control_works.all():
                instance = Certification_control_work.objects.filter(Q(certification=certification) & Q(control_work=control_work)).first()
                job_form = CertificationJobForm(
                    data=request.POST,
                    prefix=control_work.id,
                    use_required_attribute=False,
                    initial={
                        'control_work': control_work,
                    },
                    instance=instance,
                )
                if job_form.is_valid():
                    job_instance = job_form.instance
                    job_instance.certification = certification
                    job_form.instance = job_instance
                    job_form.save()
                else:
                    if instance:
                        instance.delete()
                job_weights[control_work.id] = job_form
        bool_form.formTranslateCreate = translate_form
        bool_form.fields['is_translate'].widget = ScaleTranslateCreateWidget(
            create_form=bool_form.formTranslateCreate, 
            name='scales-translate-create', 
            choices=bool_form.PREDEFINDED_TRANSLATE_OPTIONS
            )
        subforms = []
        subforms.append(bool_form)
        return render(request, 'teacherapp/certification_detail.html', context={
            'schedule': schedule,
            'certification': certification,
            'form': form,
            'subforms': subforms,
            'job_weights': job_weights,
        })


class Certification_delete(CertificationMixin, View):
    def post(self, request, schedule_id, certification_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        certification = get_object_or_404(Certification, id=certification_id)
        certification.delete()
        messages.success(request, 'Аттестация успешно удалена!')
        return redirect(reverse("teacherapp_control_type_list_url", kwargs={
            "schedule_id": schedule.id, 
            }))


class Certification_write(LoginScheduleRequiredMixin, View):
    def get(self, request, schedule_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        return redirect(reverse('teacherapp_certification_list_url', kwargs={
            "schedule_id": schedule.id, 
            }))

class Certification_write_detail(CertificationMixin, View):
    def get_normal_grade_verification(self, input): # перевод из n-балльной шкалы в 5-балльную
        grade = input.grade
        if not grade:
            grade = 0
        dimension = input.controlwork.scale.dimension
        if input.controlwork.scale.to_five: # если есть перевод шкалы
            translate = input.controlwork.scale.to_five
            if grade > translate.good and grade <= translate.perfectly:
                return 5
            elif grade > translate.satisfactorily:
                return 4
            elif grade > translate.badly:
                return 3
            elif grade >= 0:
                return 2
            else:
                return 0
        else:
            return get_grade_from_procent(grade*100/dimension)

    def get_grade(self, grade):   # перевод в 5-балльной шкале
        if grade.controlwork.scale.dimension == 2:
            if grade.grade == 2:
                return 5
            else:
                return 2
        elif grade.controlwork.scale.dimension == 5:
            return grade.grade
        else:
            return self.get_normal_grade_verification(grade)

    def get_grade_point(self, grade):   # перевод в 100-балльной шкале
        grade_value = grade.grade
        if not grade_value:
            grade_value = 0
        if grade.controlwork.scale.dimension == 2:
            if grade_value == 2:
                return 100
            else:
                return 0
        elif grade.controlwork.scale.dimension == 5:
            return grade_value / 5.0 * 100.0
        else:
            return grade_value*100/grade.controlwork.scale.dimension

    def get_recommened_grade(self, get_grade_function, certification, student):
        total_sum = 0
        total_weight = 0
        for certification_job in certification.certification_control_works.all():
            try:
                grade = certification_job.control_work.control_work_grades.get(student=student)
                total_sum += get_grade_function(grade) * certification_job.weight
                total_weight += certification_job.weight
            except Control_work_grade.DoesNotExist:
                grade = None
                total_sum += 0
                total_weight += certification_job.weight
        if not total_weight:
            total_weight = 1
        return round(total_sum/total_weight)

    def get_normal_grade_certification(self, input, certification):
        grade = input
        translate = certification.scale_translate
        if grade > translate.good and grade <= translate.perfectly:
            return 5
        elif grade > translate.satisfactorily:
            return 4
        elif grade > translate.badly:
            return 3
        elif grade >= 0:
            return 2
        else:
            return 0

    def get(self, request, schedule_id, certification_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        certification = get_object_or_404(Certification, id=certification_id)
        students = Student.objects.filter(studentgroup__schedule__id=schedule.id).distinct()
        jobs_elements = {}
        grade_forms = {}
        recomended_grades = {}
        for student in students:
            grades = Control_work_grade.objects.filter(student=student, controlwork__control_type__schedule__id=schedule.id).order_by('controlwork__work_number')
            jobs_elements[student.id] = grades
            certification_grade = Certification_control_work_grade.objects.filter(Q(certification=certification) & Q(student=student)).first()
            if certification.scale_translate: # если есть перевод шкалы (в 100-балльной системе)
                recomended_grades[student.id] = self.get_recommened_grade(self.get_grade_point, certification, student)
                grade_form = CertificationGradeFormPoints(
                    prefix=student.id,
                    initial={
                        'certification': certification,
                        'student': student,
                    },
                    instance=certification_grade,
                    )
            else:
                recomended_grades[student.id] = self.get_recommened_grade(self.get_grade, certification, student)
                grade_form = CertificationGradeForm(
                    prefix=student.id,
                    initial={
                        'certification': certification,
                        'student': student,
                    },
                    instance=certification_grade,
                    )
            if not certification_grade:
                grade_form.initial['grade'] = recomended_grades[student.id]
            grade_forms[student.id] = grade_form
        return render(request, 'teacherapp/certification_write.html', context={
            'schedule': schedule,
            'certification': certification,
            'jobs_elements': jobs_elements,
            'grades': grade_forms,
            'recomended_grades': recomended_grades,
        })

    def post(self, request, schedule_id, certification_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        certification = get_object_or_404(Certification, id=certification_id)
        students = Student.objects.filter(studentgroup__schedule__id=schedule.id).distinct()
        jobs_elements = {}
        grade_forms = {}
        recomended_grades = {}
        is_success = True
        for student in students:
            grades = Control_work_grade.objects.filter(student=student, controlwork__control_type__schedule__id=schedule.id).order_by('controlwork__work_number')
            jobs_elements[student.id] = grades
            certification_grade = Certification_control_work_grade.objects.filter(Q(certification=certification) & Q(student=student)).first()
            if certification.scale_translate: # если есть перевод шкалы (в 100-балльной системе)
                recomended_grades[student.id] = self.get_recommened_grade(self.get_grade_point, certification, student)
                grade_form = CertificationGradeFormPoints(
                    data=request.POST,
                    prefix=student.id,
                    initial={
                        'certification': certification,
                        'student': student,
                    },
                    instance=certification_grade,
                    )
            else:
                recomended_grades[student.id] = self.get_recommened_grade(self.get_grade, certification, student)
                grade_form = CertificationGradeForm(
                    data=request.POST,
                    prefix=student.id,
                    initial={
                        'certification': certification,
                        'student': student,
                    },
                    instance=certification_grade,
                    )
            if not certification_grade:
                grade_form.initial['grade'] = recomended_grades[student.id]
            if grade_form.is_valid():
                grade_form.save()
                if certification.scale_translate:   
                    new_instance = grade_form.instance
                    new_instance.grade = self.get_normal_grade_certification(new_instance.grade, certification)
                    grade_form.instance = new_instance
                    grade_form.save()
            else:
                is_success = False
            grade_forms[student.id] = grade_form
        if is_success:
            messages.success(request, 'Аттестация успешно сохранена!')
            if certification.scale_translate:
                scale_translate = certification.scale_translate
                certification.scale_translate = None
                certification.save()
                scale_translate.delete()
        return HttpResponseRedirect(request.path_info)