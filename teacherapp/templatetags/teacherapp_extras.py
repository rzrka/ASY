from django import template
from datetime import datetime, timedelta
from django.conf import settings
from django.db.models import Q, Count

from dateutil import tz 
from dateutil.parser import parse
from pytz import timezone
from teacherapp.forms import GradeAttendanceFormOffset
from teacherapp.views import get_grade_from_procent
from mainapp.models import TeleWork, Certification_control_work, Certification, Certification_control_work_grade
import re


register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


'''str to tuple'''
@register.filter
def get_tuple(input):
    try:
        input = eval(input)
        return input[0]
    except:
        if len(input) > 0:
            if input[0] == '(':
                return tuple(input)[0]
        return input


'''Создает конечную дату'''
@register.filter
def return_term(input):
    plus_timedelta = TeleWork.TIMEDELTA
    input = input.replace(tzinfo=None) + plus_timedelta
    return input


'''Возвращает оставшееся время'''
@register.filter
def create_term(input):
    back = return_term(input)  - datetime.now()
    days, seconds = back.days, back.seconds
    hours = seconds // 3600
    if days<0:  # если дней отрицательное количество
        return 'работа просрочена!'
    if days>=1:
        result = '> 1дня'
    elif hours>=4:
        result = '< 1дня'
    elif hours>=1:
        result = '< 4 часов'
    else:
        result = '< 1 часа'
    return result


'''Возвращает оценку для цвета'''
@register.filter
def create_term_class(input):
    back = return_term(input)  - datetime.now()
    days, seconds = back.days, back.seconds
    hours = seconds // 3600
    if days<0:  # если дней отрицательное количество
        return '2'
    if days>=1:
        result = '5'
    elif hours>=4:
        result = '4'
    elif hours>=1:
        result = '3'
    else:
        result = '2'
    return result


@register.filter
def grade_attendance_offset(input):
    choices = GradeAttendanceFormOffset.Meta.choices
    for choice in choices:
        if choice[0] == input.grade:
            return choice[1]
    return "0"


@register.filter
def grade_attendance_offset_grade(input):
    if input.grade == 0:
        return 2
    elif input.grade == 2:
        return 5
    else:
        return "0"
        

'''получение оценки из n-балльной шкалы'''
@register.filter
def get_normal_grade(input):
    try:
        grade = input.grade
    except AttributeError:
        return 0
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
            return "Error. Grade not found!"
    else:
        return get_grade_from_procent(grade*100/dimension)
        


@register.filter
def get_normal_grade_verification(input):
    grade = input.grade
    dimension = input.control_grade.controlwork.scale.dimension
    if input.control_grade.controlwork.scale.to_five: # если есть перевод шкалы
        translate = input.control_grade.controlwork.scale.to_five # было input.controlwork.scale.to_five
        if grade > translate.good and grade <= translate.perfectly:
            return 5
        elif grade > translate.satisfactorily:
            return 4
        elif grade > translate.badly:
            return 3
        elif grade >= 0:
            return 2
        else:
            return "Error. Grade not found!"
    elif dimension == 100:
        return get_grade_from_procent(grade)
    else:
        return get_grade_from_procent(grade*100/dimension)
    

'''получение оценки стуента из всех его оценок'''
@register.filter
def get_by_student(grades, student):
    grade = grades.filter(student=student).first()
    return grade


'''Query filter'''
@register.filter
def general_criterions(verification):
    return verification.tele_work_criterions.filter(criterion__is_subcriterion=False).order_by('criterion__criterion_number')


'''Query filter'''
@register.filter
def subcriterions(verification_criterion, verification):
    subcriterions = verification.tele_work_criterions.filter(criterion__is_subcriterion=True)
    criterion = verification_criterion.criterion
    return subcriterions.filter(criterion__subcriterion=criterion)


'''Query filter'''
@register.filter
def unread_comments(attendance, user):
    return attendance.comments.filter(Q(is_readed=False) & ~Q(author=user))


'''Query filter'''
@register.filter
def unchecked_works(attendance):
    try:
        return attendance.tele_works.filter(is_checked=False)
    except AttributeError:
        return 0


'''Get value from input filter'''
@register.filter
def get_value(input):
    return "checked" in  input


'''Remove word from string'''
@register.filter
def remove_word(input, word):
    return input.replace(word, '')


'''Return bool is work in certification'''
@register.filter
def is_certification_work(certification, work):
    queryset = Certification.objects.filter(Q(id=certification) & Q(certification_control_works__control_work__id=work))
    return queryset


@register.filter
def get_normal_grade_certification(input, certification):
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
        return "Error. Grade not found!"


'''Query filter'''
@register.filter
def get_grade_from_queryset(grades, student):
    try:
        return grades.get(student=student)
    except Certification_control_work_grade.DoesNotExist:
        return "?"
    

@register.filter
def get_unchecked_student_comments(criterions):
    rez = 0
    for criterion in criterions:
        rez += criterion.tele_work_criterion_comment.filter(is_checked=False).count()
    return rez


@register.filter
def get_unchecked_teacher_comments(criterions):
    rez = 0
    for criterion in criterions:
        rez += criterion.tele_work_criterion_comment_student.filter(is_checked=False).count()
    return rez
    

@register.filter
def get_unchecked_student_comments_grade(grade):
    for telework in grade.tele_works.filter(is_checked=True):
        for criterion in telework.tele_work_criterions.all():
            if criterion.tele_work_criterion_comment.filter(is_checked=False).count():
                return 1
    return 0
    

@register.filter
def get_unchecked_student_comments_job(verification):
    grade = verification.control_grade
    for telework in grade.tele_works.filter(is_checked=True):
        for criterion in telework.tele_work_criterions.all():
            if criterion.tele_work_criterion_comment_student.filter(is_checked=False).count():
                return 1
    return 0


@register.filter
def get_grade_from_query(grades, job):
    return grades.filter(controlwork=job).first()


@register.filter
def get_history_verification(queryset, student):
    verification =  queryset.filter(Q(control_grade__student=student) & Q(is_checked=True)).order_by('check_date').last()
    return verification


@register.filter
def get_expansion(filename):
    list_expansions = ['txt', 'pdf', 'xlsx', 'xls', 'doc', 'docx', 'dot', 'exe', 'jpg'
    ,'rar', 'png', 'xml', 'zip']
    filename = filename.__str__()
    index = filename.rfind('.') 
    expansion = filename[(index+1):]
    if not expansion in list_expansions:
        expansion = 'None'
    return expansion


@register.filter
def get_last_verification(grade):
    verification = grade.tele_works.all().last()
    return verification.files


@register.filter
def n_replace(string, value):
    return string.replace('{N}', str(value))