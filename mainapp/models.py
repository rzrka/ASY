from django.db import models
from django.shortcuts import reverse
from django.conf import settings
from django.utils import timezone
from django.utils.text import Truncator

import os
import datetime
from datetime import datetime as time
from datetime import timedelta
from users.models import CustomUser as User


# Create your models here.
# new User model
# class CustomUser(AbstractUser):
#     pass
    # class Meta:
    #     proxy = True

    # def get_full_name(self):
    #     return ""


# Возвращает название сезона
def get_season(date_start, date_end):
    mid_val = date_end-date_start
    mid_val /= 2
    date = date_start + mid_val
    month = date.month
    if month in [1,2,12]:
        return 'winter'
    elif month in [3,4,5]:
        return 'spring'
    elif month in [6,7,8]:
        return 'summer'
    elif month in [9,10,11]:
        return 'fall'

class Semester(models.Model):
    name = models.CharField(max_length=50, blank=True, unique=True, verbose_name='Название')
    date_start = models.DateField(verbose_name='Дата начала')
    date_end = models.DateField(verbose_name='Дата окончания')

    class Meta:
        verbose_name = 'семестр'
        verbose_name_plural = 'семестры'

    def __str__(self):
        return self.name

    def save(self,*args, **kwargs):
        if not self.id:
            pre_name = "{date_start}/{date_end} ({season})".format(date_start = self.date_start.year
            , date_end = self.date_end.year % 100
            , season=get_season(self.date_start, self.date_end))
            self.name=self.name if self.name else pre_name
        super().save(*args, **kwargs)

    # def get_absolute_url(self):
    #     return reverse("post_detail_url", kwargs={"slug": self.slug})


class EducationalEstablishment(models.Model):
    full_name = models.CharField(max_length=50, unique=True, verbose_name='Полное название')
    abbreviation = models.CharField(max_length=50, unique=True, verbose_name='Аббревиатура')

    class Meta:
        verbose_name = 'образовательное учреждение'
        verbose_name_plural = 'образовательные учреждения'

    def __str__(self):
        return "{abbreviation}({full_name})".format(full_name=self.full_name, abbreviation=self.abbreviation)


class Discipline(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    semesters = models.ManyToManyField('Semester', related_name='disciplines', through='Schedule', verbose_name='Семестр') #related_name='disciplines'
    studentgroups = models.ManyToManyField('StudentGroup', related_name='disciplines', through='Schedule', verbose_name='Группа') #related_name='disciplines'

    class Meta:
        verbose_name = 'дисциплина'
        verbose_name_plural = 'дисциплины'

    def __str__(self):
        return self.name


class StudentGroup(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Название')
    year_start_studing = models.IntegerField(verbose_name='Год начала обучения')
    year_end_studing = models.IntegerField(verbose_name='Год окончания обучения')
    specialty = models.CharField(max_length=50, blank=True, verbose_name='Специальность')
    educationalestablishment = models.ForeignKey(EducationalEstablishment, on_delete=models.CASCADE, verbose_name='Образовательное учреждение')

    class Meta:
        verbose_name = 'группа'
        verbose_name_plural = 'группы'

    def __str__(self):
        return self.name


class Student(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Студент', related_name='students')
    studentgroup = models.ForeignKey(StudentGroup, on_delete=models.CASCADE, verbose_name='Группа', related_name='students')

    version_in_group = models.IntegerField(blank=True, verbose_name='Номер варианта в группе')

    class Meta:
        verbose_name = 'студент'
        verbose_name_plural = 'студенты'

    def save(self,*args, **kwargs):
        if not self.id:
            self.version_in_group = self.version_in_group if self.version_in_group else 0
        super().save(*args, **kwargs)

    def __str__(self):
        return self.student.username

    def __unicode__(self):
        return self.student.get_full_name() 


class Teacher(models.Model):
    teacher = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Преподаватель', related_name='teachergroup')
    teachergroup = models.ForeignKey(StudentGroup, blank=True, null=True, on_delete=models.CASCADE, verbose_name='Курируемая группа', related_name='teachergroup')

    class Meta:
        verbose_name = 'преподаватель'
        verbose_name_plural = 'преподаватели'

    def __str__(self):
        return self.teacher.username


class Schedule(models.Model):
    absolute_journal_name = models.CharField(max_length=200, blank=True, unique=True) # проверка наличия журнала

    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE, verbose_name='Дисциплина')
    studentgroup = models.ForeignKey(StudentGroup, on_delete=models.CASCADE, verbose_name='Группа')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, verbose_name='Семестр')
    user = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='Преподаватель')

    class Meta:
        verbose_name = 'журнал'
        verbose_name_plural = 'журналы'

    def __str__(self):
        return self.semester.__str__() + ' ' + self.discipline.__str__() + ' ' + self.studentgroup.__str__() + ' ' + self.studentgroup.educationalestablishment.abbreviation

    def save(self,*args, **kwargs):
        if not self.id:
            self.absolute_journal_name = "{semester}_{discipline}_{studentgroup}_{educationalestablishment}_{user}".format(
                semester = self.semester.__str__()
                , discipline = self.discipline.__str__()
                , studentgroup = self.studentgroup.__str__()
                , user = self.user.id
                , educationalestablishment = self.studentgroup.educationalestablishment.abbreviation
            )
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("teacherapp_schedule_detail_url", kwargs={"schedule_id": self.id})


class AuditoryLessons(models.Model):
    TYPES_EMPLOYMENT = (
        ('Лек.', 'Лекция'),
        ('ЛР', 'Лабораторная работа'),
        ('ПР', 'Практическая работа'),
    )
    date = models.DateField(default=datetime.date.today, verbose_name='Дата занятия')
    lessons_number = models.IntegerField(blank=True, verbose_name='Номер занятия')
    theme = models.TextField(max_length=200, blank=True, verbose_name='Тема занятия')
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, verbose_name='Журнал', related_name='auditoryLessons')
    type_employment = models.CharField(max_length=50, choices=TYPES_EMPLOYMENT, default=TYPES_EMPLOYMENT[0], verbose_name='Вид занятия') # будет ссылка на хз короч / blank=True

    class Meta:
        verbose_name = 'занятие'
        verbose_name_plural = 'занятия'

    def __str__(self):
        return "Занятие №{lessons_number}, от {date}, вид занятия: \"{type_employment}\", тема: \"{theme}\"".format(
            date=self.date.strftime("%d.%m.%Y"),
            lessons_number=self.lessons_number,
            type_employment = self.type_employment,
            theme = 'Не указано' if not self.theme else Truncator(self.theme).words(5),
        )

    def get_increment_lesson(self):
        pass
    
    def get_absolute_url(self):
        return reverse("teacherapp_lesson_detail_url", kwargs={"schedule_id": self.schedule.id, 'lesson_id': self.id})

    def get_delete_url(self):
        return reverse("teacherapp_lesson_delete_url", kwargs={"schedule_id": self.schedule.id, 'lesson_id': self.id})


class AuditoryAttendance(models.Model):
    ATTENDANCE_GRADES = (
        ('+', 'Присутствует'),
        ('нб.', 'Отсутствует'),
        ('нб.(ув.)', 'Отсутствует (по уважительной причине)'),
        ('?', 'Не отмечено'),
    )

    absolute_attendance_name = models.CharField(max_length=200, blank=True, unique=True) # проверка наличия оценки

    grade = models.CharField(max_length=50, blank=False, default=ATTENDANCE_GRADES[3], choices=ATTENDANCE_GRADES,verbose_name='Оценка посещаемости')
    # user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Студент')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='Студент', related_name='auditoryAttendance')
    auditorylessons = models.ForeignKey(AuditoryLessons, on_delete=models.CASCADE, verbose_name='Занятие', related_name='auditoryAttendance')

    class Meta:
        verbose_name = 'оценка посещаемости занятия'
        verbose_name_plural = 'оценки посещаемости занятия'

    def __str__(self):
        return self.grade

    def save(self,*args, **kwargs):
        if not self.id:
            self.absolute_attendance_name = "{user}_{auditorylessons}".format(
                user = self.student.id
                , auditorylessons = self.auditorylessons.id
            )
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("teacherapp_lesson_student_attendance_detail_url", kwargs={
            "schedule_id": self.auditorylessons.schedule.id, 
            'lesson_id': self.auditorylessons.id, 
            'grade_id': self.id})


class Comment(models.Model):
    attendance = models.ForeignKey(AuditoryAttendance, on_delete=models.CASCADE, verbose_name="Оценка посещаемости", related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь", related_name='comments')
    message = models.TextField(max_length=500, verbose_name="Сообщение")
    pub_date = models.DateTimeField(verbose_name='Дата сообщения', default=timezone.now)
    is_readed = models.BooleanField(verbose_name='Прочитано', default=False)
    files = models.ManyToManyField('File', blank=True, related_name='comments')
 
    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
        ordering=['pub_date']
 
    def __str__(self):
        return self.message


class File(models.Model):
    file = models.FileField(upload_to=settings.DEFAULT_FILE_STORAGE, verbose_name="файл")

    class Meta:
        verbose_name = 'файл'
        verbose_name_plural = 'файлы'
 
    def __str__(self):
        return os.path.basename(self.file.name)


class ControlScaleTranslate(models.Model):
    perfectly = models.IntegerField(blank=False, default=100, verbose_name='Отлично')
    good = models.IntegerField(blank=False, default=80, verbose_name='Хорошо')
    satisfactorily = models.IntegerField(blank=False, default=60, verbose_name='Удовлетворительно')
    badly = models.IntegerField(blank=False, default=40, verbose_name='Неудовлетворительно')

    class Meta:
        verbose_name = 'перевод шкалы контроля'
        verbose_name_plural = 'переводы шкалы контроля'

    def __str__(self):
        return "Переводчик шкалы контроля"


class ControlScale(models.Model):
    DIMENSION_CHOICES = (
        (2, 'зачет/незачет'),
        (5, '5-балльная'),
        (100, '100-балльная'),
    )
    dimension = models.IntegerField(blank=False, verbose_name='Размерность')
    to_five = models.OneToOneField(ControlScaleTranslate, verbose_name='Перевод из N-балльной в 5-балльную', 
        on_delete=models.SET_NULL, blank=True, null=True, default=None, related_name='control_scale')

    class Meta:
        verbose_name = 'шкала контроля'
        verbose_name_plural = 'шкалы контроля'

    def delete(self, *args, **kwargs):
        if self.to_five:
            self.to_five.delete()
        return super(self.__class__, self).delete(*args, **kwargs)

    def __str__(self):
        return "{dimension}-балльная".format(
            dimension = self.dimension,
        )


class ControlCriterion(models.Model):
    criterion_number = models.IntegerField(default=0, blank=True, verbose_name='Номер критерия')
    name = models.CharField(max_length=50, blank=False, verbose_name='Название')
    weight = models.IntegerField(default=0, verbose_name='Вес критерия')
    subcriterion = models.ManyToManyField("self", blank=True, default=None, verbose_name='Подкритерии', related_name='control_criterions') # подкритерии
    # если это подкритерий, то шкала ему не нужна (хотя пх-пх)!
    scale = models.OneToOneField(ControlScale, blank=True, null=True, on_delete=models.CASCADE, verbose_name='Шкала', related_name='criterion') # шкала
    is_subcriterion = models.BooleanField(verbose_name='Это подкритерий', default=False)

    class Meta:
        verbose_name = 'критерий контроля'
        verbose_name_plural = 'критерии контроля'

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        if not self.is_subcriterion:
            for subcrit in self.subcriterion.all():
                subcrit.delete()
        try: # хз почему, но выдает ошибку при массовом удалении
            if self.scale:
                self.scale.delete()
        except:
            pass
        return super(self.__class__, self).delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("teacherapp_control_type_criterion_detail_url", kwargs={
            "schedule_id": self.control_works.all()[0].control_type.schedule.id, 
            'control_type_id': self.control_works.all()[0].control_type.id,
            'job_id': self.control_works.all()[0].id,
            'criterion_id': self.id,
            })

    def get_delete_url(self):
        return reverse("teacherapp_control_type_criterion_delete_url", kwargs={
            "schedule_id": self.control_works.all()[0].control_type.schedule.id, 
            'control_type_id': self.control_works.all()[0].control_type.id,
            'job_id': self.control_works.all()[0].id,
            'criterion_id': self.id,
            })


class ControlType(models.Model):
    # Предопределенные имена
    PREDEFINDED_NAMES = (
        ('Тест', 'Тест'),
        ('Устный опрос', 'Устный опрос'),
        ('Отчет по лабораторной работе', 'Отчет по лабораторной работе'),
    )
    name = models.CharField(max_length=50, blank=False, verbose_name='Название') #, choices=ATTENDANCE_GRADES
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, verbose_name="Журнал", related_name='control_types')
    lesson = models.OneToOneField(AuditoryLessons, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Привязанное занятие", related_name='control_type')
    distance_work_check = models.BooleanField(verbose_name='Дистанционная проверка работ', default=False)
    have_general_criterions = models.BooleanField(blank=False, default=False, verbose_name='Имеет ли общие критерии для всего вида контроля')
    criterions = models.ManyToManyField(ControlCriterion, blank=True, default=None, verbose_name='Критерии', related_name='control_type')

    class Meta:
        verbose_name = 'вид контроля'
        verbose_name_plural = 'виды контроля'

    def delete(self, *args, **kwargs):
        for criterion in self.criterions.all():
            criterion.delete()
        for control_work in self.control_works.all():
            control_work.delete()
        return super(self.__class__, self).delete(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("teacherapp_control_type_detail_url", kwargs={"schedule_id": self.schedule.id, 'control_type_id': self.id})

    def get_delete_url(self):
        return reverse("teacherapp_control_type_delete_url", kwargs={"schedule_id": self.schedule.id, 'control_type_id': self.id})


class ControlWork(models.Model):
    work_number = models.IntegerField(blank=True, default=0, verbose_name='Номер работы')
    name = models.TextField(max_length=200, blank=False, verbose_name='Название')
    control_type = models.ForeignKey(ControlType, on_delete=models.CASCADE, verbose_name="Вид контроля", related_name='control_works')
    weight = models.IntegerField(default=0, verbose_name='Вес работы')
    criterions = models.ManyToManyField(ControlCriterion, blank=True, default=None, verbose_name='Критерии', related_name='control_works')
    # шкала работы по виду контроля (у каждой работы своя шкала, по ней осуществляется перевод в 5-балльную шкалу)
    scale = models.OneToOneField(ControlScale, blank=False, on_delete=models.CASCADE, verbose_name='Шкала', related_name='control_work') 

    class Meta:
        verbose_name = 'работа'
        verbose_name_plural = 'работы'

    def delete(self, *args, **kwargs):
        for criterion in self.criterions.all():
            criterion.delete()
        for control_work_grade in self.control_work_grades.all():
            control_work_grade.delete()
        try: # хз почему, но выдает ошибку при массовом удалении
            if self.scale:
                self.scale.delete()
        except:
            pass
        return super(self.__class__, self).delete(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("teacherapp_control_type_job_detail_url", kwargs={
            "schedule_id": self.control_type.schedule.id, 
            'control_type_id': self.control_type.id,
            'job_id': self.id,
            })

    def get_delete_url(self):
        return reverse("teacherapp_control_type_job_delete_url", kwargs={
            "schedule_id": self.control_type.schedule.id, 
            'control_type_id': self.control_type.id,
            'job_id': self.id,
            })


class Control_work_grade(models.Model):
    STATUS_VARIANTS = (                         # варианты статуса проверки
        ('Не отправлялась на проверку', 'Не отправлялась на проверку'),       # если объектов нет
        ('Отправлена на проверку {N}-й раз', 'Отправлена на проверку {N}-й раз'),
        ('Зачтена', 'Зачтена'),
        ('Проверена {N}-й раз (есть замечания)', 'Проверена {N}-й раз (есть замечания)'),
    )
    # STATUS_VARIANTS = (                         # варианты статуса проверки
    #     ('Не сдавалась', 'Не сдавалась'),       # если объектов нет
    #     ('Сдавалась', 'Сдавалась'),
    #     ('Зачет', 'Зачет'),
    # )
    grade = models.IntegerField(blank=True, null=True, verbose_name='Оценка за работу')                                 # сама оценка
    #translated_grade = models.IntegerField(blank=True, null=True, verbose_name='Переведенная оценка за работу')        # переведенная в 5-балльную шкалу оценка
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='Студент', related_name='control_work_grades')
    controlwork = models.ForeignKey(ControlWork, on_delete=models.CASCADE, verbose_name='Работа', related_name='control_work_grades')
    status = models.CharField(max_length=100, blank=False, default=STATUS_VARIANTS[0], verbose_name='Статус', choices=STATUS_VARIANTS)

    class Meta:
        verbose_name = 'оценка контроля студентов'
        verbose_name_plural = 'оценки контроля студентов'

    def __str__(self):
        if self.grade:
            return str(self.grade)
        return "0"

    # def save(self,*args, **kwargs):
    #     if not self.id:
    #         if not self.translated_grade:
    #             self.translated_grade = self.id
    #     super().save(*args, **kwargs)


'''Создается при отправке документа на проверку преподователю'''
class TeleWork(models.Model):
    COMPLERION_DAYS = 2                         # количество дней проверки
    TIMEDELTA = timedelta(days=COMPLERION_DAYS) # объект timedelta с заданным количеством дней

    delivery_date = models.DateTimeField(verbose_name='Время сдачи на проверку', auto_now_add=True)
    check_date = models.DateTimeField(verbose_name='Время проверки', blank=True, null=True)
    # term = models.DateTimeField(verbose_name='Срок проверки', default=time.now()+timedelta(days=2))
    control_grade = models.ForeignKey(Control_work_grade, on_delete=models.CASCADE, verbose_name='Оценка, привязанная к проверке', related_name='tele_works')
    files = models.ForeignKey(File, on_delete=models.CASCADE, verbose_name='Файл',  related_name='tele_works')
    # is_best = models.BooleanField(verbose_name='Лучшая работа', default=False)  # является ли лучшей работой
    is_checked = models.BooleanField(verbose_name='Проверена ли работа', default=False)
    grade = models.IntegerField(blank=False, default=0, verbose_name='Оценка за работу')   # оценка за данную работу
    additional_comment = models.TextField(max_length=500, blank=True, null=True, verbose_name="Дополнительное примечание")
    additional_comment_student = models.TextField(max_length=500, blank=True, null=True, verbose_name="Дополнительное примечание студента")
    
    class Meta:
        verbose_name = 'работа на проверку'
        verbose_name_plural = 'работы на проверку'
        
    def save(self,*args, **kwargs):
        if not self.id:
            unchecked_works = self.control_grade.tele_works.filter(is_checked=False)
            for unchecked_work in unchecked_works:
                unchecked_work.delete()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.delivery_date.strftime("%d-%b-%Y (%H:%M:%S)")

    def get_absolute_url(self):
        return reverse("teacherapp_works_verification_detail_url", kwargs={
            "verification_id": self.id, 
            })


'''Создается вместе с TeleWork, в зависимости от критериев'''
class TeleWorkCriterions(models.Model):
    telework = models.ForeignKey(TeleWork, on_delete=models.CASCADE, verbose_name='Работа на проверку', related_name='tele_work_criterions')
    criterion = models.ForeignKey(ControlCriterion, on_delete=models.CASCADE, verbose_name='Критерий', related_name='tele_work_criterions')
    grade = models.IntegerField(default=0, verbose_name='Оценка за работу')

    class Meta:
        verbose_name = 'критерий работы на проверку'
        verbose_name_plural = 'критерии работы на проверку'

    def __str__(self):
        return str(self.grade)


'''Комментарий по TeleWorkCriterions'''
class TeleWorkCriterionsComment(models.Model):
    text = models.TextField(max_length=500, blank=False, verbose_name="Коммент")
    comment_type = models.TextField(max_length=100, verbose_name="Типовое замечание")
    teleworkcriterion = models.ForeignKey(TeleWorkCriterions, blank=False, on_delete=models.CASCADE, verbose_name='Критерий работы на проверку', related_name='tele_work_criterion_comment')
    is_checked = models.BooleanField(verbose_name='Просмотрен ли комментарий', default=False)

    class Meta:
        verbose_name = 'комментарий критерия работы на проверку'
        verbose_name_plural = 'комментарии критерия работы на проверку'

    def __str__(self):
        return self.text


'''Комментарий по TeleWorkCriterions от студента'''
class TeleWorkCriterionsCommentStudent(models.Model):
    text = models.TextField(max_length=500, blank=False, verbose_name="Коммент")
    teleworkcriterion = models.ForeignKey(TeleWorkCriterions, blank=False, on_delete=models.CASCADE, verbose_name='Критерий работы на проверку', related_name='tele_work_criterion_comment_student')
    is_checked = models.BooleanField(verbose_name='Просмотрен ли комментарий', default=False)

    class Meta:
        verbose_name = 'комментарий критерия работы на проверку от студента'
        verbose_name_plural = 'комментарии критерия работы на проверку от студентов'

    def __str__(self):
        return self.text


'''Аттестация'''
class Certification(models.Model):
    CERTIFICATION_TYPES = (
        ('Текущая аттестация', 'Текущая аттестация'),
        ('Промежуточная аттестация', 'Промежуточная аттестация'),
    )
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, verbose_name='Журнал', related_name='certifications')
    number = models.IntegerField(blank=False, default=0, verbose_name='Номер')
    name = models.CharField(max_length=100, blank=False, verbose_name='Название')
    type = models.CharField(max_length=50, blank=False, default=CERTIFICATION_TYPES[0], verbose_name='Вид', choices=CERTIFICATION_TYPES)
    scale_translate = models.OneToOneField(ControlScaleTranslate, verbose_name='Перевод из 100-балльной в 5-балльную', 
        on_delete=models.SET_NULL, blank=True, null=True, default=None, related_name='certification')

    class Meta:
        verbose_name = 'аттестация'
        verbose_name_plural = 'аттестации'

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        try: # хз почему, но выдает ошибку при массовом удалении
            if self.scale_translate:
                self.scale_translate.delete()
        except:
            pass
        return super(self.__class__, self).delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("teacherapp_certification_detail_url", kwargs={
            "schedule_id": self.schedule.id, 
            "certification_id": self.id,
            })

    def get_delete_url(self):
        return reverse("teacherapp_certification_delete_url", kwargs={
            "schedule_id": self.schedule.id, 
            "certification_id": self.id,
            })


'''Работы с аттестацией'''
class Certification_control_work(models.Model):
    certification = models.ForeignKey(Certification, blank=False, on_delete=models.CASCADE, verbose_name='Аттестация', related_name='certification_control_works')
    control_work = models.ForeignKey(ControlWork, blank=False, on_delete=models.CASCADE, verbose_name='Работа', related_name='certification_control_works')
    weight = models.IntegerField(default=0, verbose_name='Вес работы')

    class Meta:
        verbose_name = 'работа с аттестацией'
        verbose_name_plural = 'работы с аттестацией'

    def __str__(self):
        return str(self.weight)


'''Оценка работы с аттестацией'''
class Certification_control_work_grade(models.Model):
    certification = models.ForeignKey(Certification, blank=False, on_delete=models.CASCADE, verbose_name='Аттестация', related_name='certification_control_work_grades')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=True, verbose_name='Студент', related_name='certification_control_work_grades')
    grade = models.IntegerField(default=0, verbose_name='Оценка за работу')

    class Meta:
        verbose_name = 'оценка работы с аттестацией'
        verbose_name_plural = 'оценки работы с аттестацией'

    def __str__(self):
        return str(self.grade)