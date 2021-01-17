# Generated by Django 3.0.8 on 2020-07-22 21:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mainapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='teacher',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='teachergroup', to=settings.AUTH_USER_MODEL, verbose_name='Преподаватель'),
        ),
        migrations.AddField(
            model_name='teacher',
            name='teachergroup',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='teachergroup', to='mainapp.StudentGroup', verbose_name='Ведомая группа'),
        ),
        migrations.AddField(
            model_name='studentgroup',
            name='educationalestablishment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.EducationalEstablishment', verbose_name='Образовательное учреждение'),
        ),
        migrations.AddField(
            model_name='student',
            name='student',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='students', to=settings.AUTH_USER_MODEL, verbose_name='Студент'),
        ),
        migrations.AddField(
            model_name='student',
            name='studentgroup',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='students', to='mainapp.StudentGroup', verbose_name='Группа'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='discipline',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.Discipline', verbose_name='Дисциплина'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='semester',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.Semester', verbose_name='Семестр'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='studentgroup',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.StudentGroup', verbose_name='Группа'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.Teacher', verbose_name='Преподаватель'),
        ),
        migrations.AddField(
            model_name='discipline',
            name='semesters',
            field=models.ManyToManyField(related_name='disciplines', through='mainapp.Schedule', to='mainapp.Semester', verbose_name='Семестр'),
        ),
        migrations.AddField(
            model_name='discipline',
            name='studentgroups',
            field=models.ManyToManyField(related_name='disciplines', through='mainapp.Schedule', to='mainapp.StudentGroup', verbose_name='Группа'),
        ),
        migrations.AddField(
            model_name='controlwork',
            name='control_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='control_works', to='mainapp.ControlType', verbose_name='Вид контроля'),
        ),
        migrations.AddField(
            model_name='controlwork',
            name='criterions',
            field=models.ManyToManyField(blank=True, default=None, related_name='control_works', to='mainapp.ControlCriterion', verbose_name='Критерии'),
        ),
        migrations.AddField(
            model_name='controlwork',
            name='scale',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='control_work', to='mainapp.ControlScale', verbose_name='Шкала'),
        ),
        migrations.AddField(
            model_name='controltype',
            name='criterions',
            field=models.ManyToManyField(blank=True, default=None, related_name='control_type', to='mainapp.ControlCriterion', verbose_name='Критерии'),
        ),
        migrations.AddField(
            model_name='controltype',
            name='lesson',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='control_type', to='mainapp.AuditoryLessons', verbose_name='Привязанное занятие'),
        ),
        migrations.AddField(
            model_name='controltype',
            name='schedule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='control_types', to='mainapp.Schedule', verbose_name='Журнал'),
        ),
        migrations.AddField(
            model_name='controlscale',
            name='to_five',
            field=models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='control_scale', to='mainapp.ControlScaleTranslate', verbose_name='Перевод из N-балльной в 5-балльную'),
        ),
        migrations.AddField(
            model_name='controlcriterion',
            name='scale',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='criterion', to='mainapp.ControlScale', verbose_name='Шкала'),
        ),
        migrations.AddField(
            model_name='controlcriterion',
            name='subcriterion',
            field=models.ManyToManyField(blank=True, default=None, related_name='_controlcriterion_subcriterion_+', to='mainapp.ControlCriterion', verbose_name='Подкритерии'),
        ),
        migrations.AddField(
            model_name='control_work_grade',
            name='controlwork',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='control_work_grades', to='mainapp.ControlWork', verbose_name='Работа'),
        ),
        migrations.AddField(
            model_name='control_work_grade',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='control_work_grades', to='mainapp.Student', verbose_name='Студент'),
        ),
        migrations.AddField(
            model_name='comment',
            name='attendance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='mainapp.AuditoryAttendance', verbose_name='Оценка посещаемости'),
        ),
        migrations.AddField(
            model_name='comment',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AddField(
            model_name='comment',
            name='files',
            field=models.ManyToManyField(blank=True, related_name='comments', to='mainapp.File'),
        ),
        migrations.AddField(
            model_name='certification_control_work_grade',
            name='certification',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certification_control_work_grades', to='mainapp.Certification', verbose_name='Аттестация'),
        ),
        migrations.AddField(
            model_name='certification_control_work_grade',
            name='student',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='certification_control_work_grades', to='mainapp.Student', verbose_name='Студент'),
        ),
        migrations.AddField(
            model_name='certification_control_work',
            name='certification',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certification_control_works', to='mainapp.Certification', verbose_name='Аттестация'),
        ),
        migrations.AddField(
            model_name='certification_control_work',
            name='control_work',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certification_control_works', to='mainapp.ControlWork', verbose_name='Работа'),
        ),
        migrations.AddField(
            model_name='certification',
            name='scale_translate',
            field=models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='certification', to='mainapp.ControlScaleTranslate', verbose_name='Перевод из 100-балльной в 5-балльную'),
        ),
        migrations.AddField(
            model_name='certification',
            name='schedule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certifications', to='mainapp.Schedule', verbose_name='Журнал'),
        ),
        migrations.AddField(
            model_name='auditorylessons',
            name='schedule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='auditoryLessons', to='mainapp.Schedule', verbose_name='Журнал'),
        ),
        migrations.AddField(
            model_name='auditoryattendance',
            name='auditorylessons',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='auditoryAttendance', to='mainapp.AuditoryLessons', verbose_name='Занятие'),
        ),
        migrations.AddField(
            model_name='auditoryattendance',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='auditoryAttendance', to='mainapp.Student', verbose_name='Студент'),
        ),
    ]
