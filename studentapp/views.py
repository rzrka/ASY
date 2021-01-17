from django.shortcuts import redirect, reverse
from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Max, Sum
from django.http import JsonResponse, HttpResponseRedirect

from .utils import *
from .forms import *
from mainapp.models import *
from teacherapp.views import get_grade_from_procent
from teacherapp.forms import AttendanceCommentForm, AttendanceFileForm, GradeCriterionFormOffsetReadonly, GradeCriterionFormReadonly, GradeCriterionFormNPointReadonly

class Index(LoginRequiredMixin, View):
    def get(self, request):
        student = get_object_or_404(Student, student=request.user)
        semesters = Semester.objects.filter(schedule__studentgroup= student.studentgroup).distinct().order_by('-date_start')
        return render(request, 'studentapp/semester_list.html', context={
                'semesters': semesters,
            })


class StudentDisciplineList(LoginRequiredMixin, View):
    def get(self, request, semester_id):
        student = get_object_or_404(Student, student=request.user)
        semester = get_object_or_404(Semester, id=semester_id)
        disciplines = Discipline.objects.filter(Q(schedule__studentgroup=student.studentgroup) & Q(schedule__semester=semester)).distinct().order_by('-name')
        return render(request, 'studentapp/discipline_list.html', context={
                'semester': semester,
                'disciplines': disciplines,
            })


class StudentScheduleDetial(LoginDisciplineMixin, View):
    def get(self, request, semester_id, discipline_id):
        student = get_object_or_404(Student, student=request.user)
        semester = get_object_or_404(Semester, id=semester_id)
        discipline = get_object_or_404(Discipline, id=discipline_id)
        schedule = Schedule.objects.get(discipline=discipline, studentgroup=student.studentgroup, semester=semester)
        attendance = {}
        for lesson in AuditoryLessons.objects.filter(schedule=schedule):
            att = AuditoryAttendance.objects.filter(Q(student=student) & Q(auditorylessons=lesson)).first()
            attendance[lesson.id] = att
        total_count = len(attendance)
        total_count = total_count if total_count else 1
        skips_count = AuditoryAttendance.objects.filter(Q(student=student) & Q(auditorylessons__schedule=schedule)).filter(Q(grade='нб.')| Q(grade='нб.(ув.)') ).count()
        bad_skips_count = AuditoryAttendance.objects.filter(Q(student=student) & Q(auditorylessons__schedule=schedule)).filter(grade='нб.').count()
        skips = ("{skips_count} ({proc}%)".format(
                    skips_count = bad_skips_count,
                    proc = round(bad_skips_count*100/total_count, 2),
                ),
                get_grade_from_procent(100-round(bad_skips_count*100/total_count, 2)))
        normal_skips = ("{skips_count} ({proc}%)".format(
                    skips_count = skips_count,
                    proc = round(skips_count*100/total_count, 2),
                ),
                get_grade_from_procent(100-round(skips_count*100/total_count, 2)))
        return render(request, 'studentapp/schedule_detail.html', context={
                'semester': semester,
                'discipline': discipline,
                'schedule': schedule,
                'attendance': attendance,
                'skips': skips,
                'normal_skips': normal_skips,
                'student': student,
            })


class StudentLessonList(LoginDisciplineMixin, View):
    def get(self, request, semester_id, discipline_id):
        student = get_object_or_404(Student, student=request.user)
        semester = get_object_or_404(Semester, id=semester_id)
        discipline = get_object_or_404(Discipline, id=discipline_id)
        schedule = Schedule.objects.get(discipline=discipline, studentgroup=student.studentgroup, semester=semester)
        attendance = {}
        for lesson in AuditoryLessons.objects.filter(schedule=schedule):
            att = AuditoryAttendance.objects.filter(Q(student=student) & Q(auditorylessons=lesson)).first()
            attendance[lesson.id] = att
        total_count = len(attendance)
        total_count = total_count if total_count else 1
        skips_count = AuditoryAttendance.objects.filter(Q(student=student) & Q(auditorylessons__schedule=schedule)).filter(Q(grade='нб.')| Q(grade='нб.(ув.)') ).count()
        bad_skips_count = AuditoryAttendance.objects.filter(Q(student=student) & Q(auditorylessons__schedule=schedule)).filter(grade='нб.').count()
        skips = ("{skips_count} ({proc}%)".format(
                    skips_count = bad_skips_count,
                    proc = round(bad_skips_count*100/total_count, 2),
                ),
                get_grade_from_procent(100-round(bad_skips_count*100/total_count, 2)))
        normal_skips = ("{skips_count} ({proc}%)".format(
                    skips_count = skips_count,
                    proc = round(skips_count*100/total_count, 2),
                ),
                get_grade_from_procent(100-round(skips_count*100/total_count, 2)))
        return render(request, 'studentapp/lesson_list.html', context={
                'semester': semester,
                'discipline': discipline,
                'schedule': schedule,
                'attendance': attendance,
                'skips': skips,
                'normal_skips': normal_skips,
            })


class StudentLessonDetail(LoginDisciplineMixin, View):
    def get(self, request, semester_id, discipline_id, lesson_id):
        student = get_object_or_404(Student, student=request.user)
        semester = get_object_or_404(Semester, id=semester_id)
        discipline = get_object_or_404(Discipline, id=discipline_id)
        schedule = Schedule.objects.get(discipline=discipline, studentgroup=student.studentgroup, semester=semester)
        lesson = get_object_or_404(AuditoryLessons, id=lesson_id)
        attendance = AuditoryAttendance.objects.get(auditorylessons=lesson, student=student)
        bound_form_comment = AttendanceCommentForm(
            initial={
                'attendance': attendance, 
                'author': request.user,
                }, 
            prefix='comment',
            )
        bound_form_file = AttendanceFileForm(use_required_attribute=False, prefix='file_form')
        for comment in attendance.comments.all().filter(~Q(author=request.user)):
            comment.is_readed = True
            comment.save()
        return render(request, 'studentapp/lesson_detail.html', context={
            'semester': semester,
            'discipline': discipline,
            'schedule': schedule,
            'lesson': lesson,
            'attendance': attendance,
            'form_comment': bound_form_comment,
            'form_file': bound_form_file,
        })

    def post(self, request, semester_id, discipline_id, lesson_id):
        student = get_object_or_404(Student, student=request.user)
        semester = get_object_or_404(Semester, id=semester_id)
        discipline = get_object_or_404(Discipline, id=discipline_id)
        schedule = Schedule.objects.get(discipline=discipline, studentgroup=student.studentgroup, semester=semester)
        lesson = get_object_or_404(AuditoryLessons, id=lesson_id)
        attendance = AuditoryAttendance.objects.get(auditorylessons=lesson, student=student)
        bound_form_comment = AttendanceCommentForm(
            request.POST, 
            initial={
                'attendance': attendance, 
                'author': request.user,
                },
            prefix='comment',
            )
        bound_form_file = AttendanceFileForm(request.POST, request.FILES,
            use_required_attribute=False, prefix='file_form')
        if bound_form_comment.is_valid():
            new_comment = bound_form_comment.save()
            messages.success(request, 'Комментарий добавлен!')
            bound_form_comment = AttendanceCommentForm(
                initial={'attendance': attendance, 'author': request.user},
                prefix='comment',
                )
            if bound_form_file.is_valid():
                new_file = bound_form_file.save()
                new_comment.files.add(new_file) # связывание комментария и файла
                messages.success(request, 'Файл отправлен!')
        bound_form_file = AttendanceFileForm(use_required_attribute=False, prefix='file_form')
        return render(request, 'studentapp/lesson_detail.html', context={
            'semester': semester,
            'discipline': discipline,
            'schedule': schedule,
            'lesson': lesson,
            'attendance': attendance,
            'form_comment': bound_form_comment,
            'form_file': bound_form_file,
        })


class StudentJobList(LoginDisciplineMixin, View):
    def get(self, request, semester_id, discipline_id):
        student = get_object_or_404(Student, student=request.user)
        semester = get_object_or_404(Semester, id=semester_id)
        discipline = get_object_or_404(Discipline, id=discipline_id)
        schedule = Schedule.objects.get(discipline=discipline, studentgroup=student.studentgroup, semester=semester)
        return render(request, 'studentapp/job_list.html', context={
                'semester': semester,
                'discipline': discipline,
                'schedule': schedule,
                'student': student,
            })
            

class StudentJobDetail(JobMixin, View):
    def get(self, request, semester_id, discipline_id, job_id):
        student = get_object_or_404(Student, student=request.user)
        semester = get_object_or_404(Semester, id=semester_id)
        discipline = get_object_or_404(Discipline, id=discipline_id)
        schedule = Schedule.objects.get(discipline=discipline, studentgroup=student.studentgroup, semester=semester)
        job = get_object_or_404(ControlWork, id=job_id)
        grade = Control_work_grade.objects.get(Q(controlwork=job) & Q(student=student))
        bound_form_file = AttendanceFileForm(prefix='file_form')

        history_verification = TeleWork.objects.filter(Q(control_grade=grade) & Q(is_checked=True)).order_by('check_date').last()
        
        grade_form = JobHistoryCommentForm(
            instance=history_verification,
            prefix='JobHistoryGradeForm',
        )
        iframe_form = TeleWorkCriterionsCommentForm(
            prefix='TeleWorkCriterionsCommentForm',
        )
        criterionsgrades = {}
        if history_verification:
            for teleworkCriterion in history_verification.tele_work_criterions.all():
                controlCriterion = teleworkCriterion.criterion
                points =  controlCriterion.scale.dimension                                   # какая шкала
                for teacher_comment in teleworkCriterion.tele_work_criterion_comment.all():
                    teacher_comment.is_checked = True
                    teacher_comment.save()
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

        return render(request, 'studentapp/job_detail.html', context={
                'semester': semester,
                'discipline': discipline,
                'schedule': schedule,
                'student': student,
                'job': job,
                'grade': grade,
                'form_file': bound_form_file,

                'history_verification': history_verification,
                'grade_form': grade_form,
                'criterionsgrades': criterionsgrades,
                'iframe_form': iframe_form,
        })

    def post(self, request, semester_id, discipline_id, job_id):
        student = get_object_or_404(Student, student=request.user)
        semester = get_object_or_404(Semester, id=semester_id)
        discipline = get_object_or_404(Discipline, id=discipline_id)
        schedule = Schedule.objects.get(discipline=discipline, studentgroup=student.studentgroup, semester=semester)
        job = get_object_or_404(ControlWork, id=job_id)
        grade = Control_work_grade.objects.get(Q(controlwork=job) & Q(student=student))

        bound_form_file = AttendanceFileForm(
            request.POST, 
            request.FILES,
            prefix='file_form',
            )
        if bound_form_file.is_valid():
            # создание новой TeleWork
            new_telework = TeleWork(
                control_grade=grade, 
                )
            new_file = bound_form_file.save()
            new_telework.files = new_file # связывание TeleWork и файла  
            new_telework.save()
            messages.success(request, 'Файл отправлен!')
            grade.status=Control_work_grade.STATUS_VARIANTS[1]
            grade.save()
            # создание критериев для telework
            for criterion in job.criterions.all():
                new_criterion = TeleWorkCriterions(
                    criterion=criterion,
                    telework=new_telework,
                )
                new_criterion.save()
            for criterion in job.control_type.criterions.all():
                new_criterion = TeleWorkCriterions(
                    criterion=criterion,
                    telework=new_telework,
                )
                new_criterion.save()
            return HttpResponseRedirect(request.path_info)
        return render(request, 'studentapp/job_detail.html', context={
                'semester': semester,
                'discipline': discipline,
                'schedule': schedule,
                'student': student,
                'job': job,
                'grade': grade,
                'form_file': bound_form_file,
        })


class StudentJobHistoryList(JobMixin, View):
    def get(self, request, semester_id, discipline_id, job_id):
        student = get_object_or_404(Student, student=request.user)
        semester = get_object_or_404(Semester, id=semester_id)
        discipline = get_object_or_404(Discipline, id=discipline_id)
        schedule = Schedule.objects.get(discipline=discipline, studentgroup=student.studentgroup, semester=semester)
        job = get_object_or_404(ControlWork, id=job_id)
        grade = Control_work_grade.objects.get(Q(controlwork=job) & Q(student=student))
        teleworks = TeleWork.objects.filter(
            control_grade=grade,
            is_checked=True,
            ).order_by('-check_date')
        return render(request, 'studentapp/job_history_list.html', context={
            'semester': semester,
            'discipline': discipline,
            'schedule': schedule,
            'student': student,
            'job': job,
            'teleworks': teleworks,
        }) 


class StudentJobHistoryDetail(HystoryJobMixin, View):
    def get(self, request, semester_id, discipline_id, job_id, history_job_id):
        student = get_object_or_404(Student, student=request.user)
        semester = get_object_or_404(Semester, id=semester_id)
        discipline = get_object_or_404(Discipline, id=discipline_id)
        schedule = Schedule.objects.get(discipline=discipline, studentgroup=student.studentgroup, semester=semester)
        job = get_object_or_404(ControlWork, id=job_id)
        grade = Control_work_grade.objects.get(Q(controlwork=job) & Q(student=student))
        history_verification = get_object_or_404(TeleWork, id=history_job_id)
        grade_form = JobHistoryCommentForm(
            instance=history_verification,
            prefix='JobHistoryGradeForm',
        )
        iframe_form = TeleWorkCriterionsCommentForm(
            prefix='TeleWorkCriterionsCommentForm',
        )
        criterionsgrades = {}
        for teleworkCriterion in history_verification.tele_work_criterions.all():
            controlCriterion = teleworkCriterion.criterion
            points =  controlCriterion.scale.dimension                                   # какая шкала
            # после студента - добавить
            for teacher_comment in teleworkCriterion.tele_work_criterion_comment.all():
                teacher_comment.is_checked = True
                teacher_comment.save()
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
        return render(request, 'studentapp/job_history_detail.html', context={
            'semester': semester,
            'discipline': discipline,
            'schedule': schedule,
            'student': student,
            'job': job,
            'history_verification': history_verification,
            'grade_form': grade_form,
            'criterionsgrades': criterionsgrades,
            'iframe_form': iframe_form,
        })

    def post(self, request, semester_id, discipline_id, job_id, history_job_id):
        history_verification = get_object_or_404(TeleWork, id=history_job_id)
        grade_form = JobHistoryCommentForm(
            data=request.POST,
            instance=history_verification,
            prefix='JobHistoryGradeForm',
        )
        if grade_form.is_valid():
            grade_form.save()
            messages.success(request, 'Комментарий успешно отправлен!')
        else:
            messages.error(request, 'Произошла ошибка при отправке комментария!')
        return HttpResponseRedirect(request.path_info)


class JobHistoryDetailAddComment(HystoryJobMixin, View):
    def post(self, request, semester_id, discipline_id, job_id, history_job_id):
        if request.is_ajax():
            input_data = request.POST
            text = input_data['text']
            teleworkcriterion = input_data['teleworkcriterion']
            teleworkcriterion = get_object_or_404(TeleWorkCriterions, id=teleworkcriterion)
            try:
                comment = TeleWorkCriterionsCommentStudent.objects.create(
                    text=text,
                    teleworkcriterion=teleworkcriterion,
                    )
                return JsonResponse({
                    'success': 'hello there',
                    'text': comment.text,
                    'teleworkcriterion': teleworkcriterion.id,
                    'comment_id': comment.id,
                    })
            except Exception as ex:
                print(str(ex))
                return JsonResponse({
                    'error': 'error',
                    })


class JobHistoryDetailDeleteComment(HystoryJobMixin, View):
    def post(self, request, semester_id, discipline_id, job_id, history_job_id):
        if request.is_ajax():
            input_data = request.POST
            teleworkcomment = input_data['teleworkcomment']
            teleworkcomment = get_object_or_404(TeleWorkCriterionsCommentStudent, id=teleworkcomment)
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
