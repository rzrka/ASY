from django import forms
from django.core.exceptions import ValidationError

from mainapp.models import *
from .fields import *

class LessonForm(forms.ModelForm):
    class Meta:
        model = AuditoryLessons
        fields = ['lessons_number', 'date', 'type_employment', 'theme', 'schedule'] # выбираются поля для формы

        widgets = {
            #attrs={'class': 'input'}
            'lessons_number': forms.TextInput(),
            'date': forms.DateInput(format=('%Y-%m-%d'),attrs={'type': 'date'}),
            'type_employment': forms.Select(), #radioselect
            'theme': forms.Textarea(),
            'schedule': forms.HiddenInput(),
        }

    # def clean_slug(self):
    #     new_slug = self.cleaned_data['slug'].lower()
    #     if new_slug == 'create':
    #         raise ValidationError('Slug may not be "Create"')
    #     if Tag.objects.filter(slug__iexact=new_slug).count():
    #         raise ValidationError('Slug must be unique! We have "{}" slug already!'.format(new_slug))
    #     return new_slug


class AuditoryAttendanceForm(forms.ModelForm):
    class Meta:
        model = AuditoryAttendance
        fields = ['grade'] # выбираются поля для формы

        widgets = {
            'grade': forms.RadioSelect(attrs={'class':''}),
        }


class AttendanceCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['message', 'attendance', 'author'] # выбираются поля для формы

        widgets = {
            'message': forms.Textarea(attrs={'placeholder': 'Комментарий'}),
            'attendance': forms.HiddenInput(),
            'author': forms.HiddenInput(),
        }


class AttendanceFileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['file'] # выбираются поля для формы

        widgets = { 
            'file': forms.FileInput(attrs={'class': 'inputfile', 'data-multiple-caption': "{count} файла выбрано"})
        }


class ControlTypesWorkWeight(forms.ModelForm):
    class Meta:
        model = ControlWork
        fields = ['weight'] # выбираются поля для формы

        widgets = { 
            'weight': forms.NumberInput(attrs={'min': '0'})
        }


class ControlTypesCriterionWeight(forms.ModelForm):
    class Meta:
        model = ControlCriterion
        fields = ['weight'] # выбираются поля для формы

        widgets = { 
            'weight': forms.NumberInput(attrs={'min': '0'})
        }


class ControlTypeCreateForm(forms.ModelForm):
    class Meta:
        model = ControlType
        fields = ['name', 'schedule', 'lesson', 'distance_work_check','have_general_criterions'] # выбираются поля для формы

        widgets = { 
            'schedule': forms.HiddenInput(),
            'distance_work_check': forms.CheckboxInput(attrs={'class': 'big_input'}),
            'lesson': forms.Select(),
            'have_general_criterions': forms.CheckboxInput(attrs={'class': 'big_input'}),
        }

    def __init__(self, *args, **kwargs):
        predefined_names_list = kwargs.pop('data_list', None)
        super(ControlTypeCreateForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget = ListTextWidget(data_list=predefined_names_list, name='predefined-names-list')
        self.fields['lesson'].label = 'Занятие'
        self.fields['lesson'].empty_label = 'Не привязывать к аудиторному занятию'
        self.fields['have_general_criterions'].label = 'Имеет общие критерии оценки'

    def save(self, commit=True):
        saved_object = super(ControlTypeCreateForm, self).save(commit=False)
        if saved_object.id:
            if not saved_object.have_general_criterions:
                for criterion in saved_object.criterions.all():
                    criterion.delete()
        if commit:
            saved_object.save()
        return saved_object



class ControlTypeScale(forms.ModelForm):
    class Meta:
        model = ControlScale
        fields = ['dimension', 'to_five'] # выбираются поля для формы

        widgets = { 
            'to_five': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        scales_list = kwargs.pop('data_list', None)
        super(ControlTypeScale, self).__init__(*args, **kwargs)
        self.fields['dimension'].widget = ListNumericWidget(data_list=scales_list, name='scales-list', attrs={'min': '0'})
        self.fields['dimension'].label = 'Шкала'
        # self.fields['to_five'].label = 'Перевод из одной шкалы в другую'
        # self.fields['to_five'].empty_label = 'Автоматически (из N-балльной в 100-балльную, затем в 5-балльную)'


'''Форма ControlScaleTranslate'''
class ScaleTranslateCreate(forms.ModelForm):
    class Meta:
        model = ControlScaleTranslate
        fields = ['perfectly', 'good', 'satisfactorily', 'badly'] # выбираются поля для формы

        widgets = { 
            'perfectly': forms.NumberInput(attrs={'class': 'input-scale-transform', 'min': 0}),
            'good': forms.NumberInput(attrs={'class': 'input-scale-transform', 'min': 0}),
            'satisfactorily': forms.NumberInput(attrs={'class': 'input-scale-transform', 'min': 0}),
            'badly': forms.NumberInput(attrs={'class': 'input-scale-transform', 'min': 0}),
        }


class ControlTypeScaleTranslate(forms.Form):
    FROM_N_TO_FIVE = 'FROM_N_TO_FIVE'
    PREDEFINDED_TRANSLATE_OPTIONS= (
        (None, 'Автоматически (из N-балльной в 100-балльную, затем в 5-балльную)'),
        (FROM_N_TO_FIVE, 'Из N-балльной в 5-балльную'),
    )

    is_translate = forms.ChoiceField(
        label='Перевод из одной шкалы в другую (укажите для каждой оценки максимальный балл)', 
        choices=PREDEFINDED_TRANSLATE_OPTIONS,
        ) # без choices не работает (не указаны допустимые значения)
    formTranslateCreate = None
    
    def __init__(self, *args, **kwargs):
        super(ControlTypeScaleTranslate, self).__init__(*args, **kwargs)
        self.fields['is_translate'].widget = forms.RadioSelect(choices=self.PREDEFINDED_TRANSLATE_OPTIONS)
        self.formTranslateCreate = ScaleTranslateCreate(prefix="ScaleTranslateCreate", use_required_attribute=False)
        self.fields['is_translate'].widget = ScaleTranslateCreateWidget(create_form=self.formTranslateCreate, 
            name='scales-translate-create', 
            choices=self.PREDEFINDED_TRANSLATE_OPTIONS)


class JobForm(forms.ModelForm):
    class Meta:
        model = ControlWork
        fields = ['work_number', 'name', 'weight', 'control_type'] # выбираются поля для формы

        widgets = { 
            'control_type': forms.HiddenInput(),
            'work_number': forms.NumberInput(attrs={'min': '1'}),
            'name': forms.Textarea(attrs={'placeholder': 'Тема'}),
            'weight': forms.NumberInput(attrs={'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super(JobForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'Тема'


class CriterionForm(forms.ModelForm):
    weight_norm = forms.CharField(required=False)

    class Meta:
        model = ControlCriterion
        fields = ['criterion_number', 'name', 'weight'] # выбираются поля для формы

        widgets = { 
            'criterion_number': forms.NumberInput(attrs={'min': '1'}),
            'name': forms.Textarea(attrs={'placeholder': 'Название'}),
            'weight': forms.NumberInput(attrs={'min': '0', 'class': 'weight'}),
        }

    def __init__(self, *args, **kwargs):
        super(CriterionForm, self).__init__(*args, **kwargs)
        self.fields['weight_norm'].label = 'Вес критерия (норм.), %'
        self.fields['weight_norm'].widget = forms.TextInput(attrs={'readonly': True, 'class': 'weight_norm'})


class ShowJob(forms.ModelForm):
    class Meta:
        model = ControlWork
        fields = ['work_number', 'name'] # выбираются поля для формы

        widgets = { 
            'work_number': forms.NumberInput(attrs={'readonly': True,}),
            'name': forms.Textarea(attrs={'readonly': True,}),
        }


'''5-балльная шкала'''
class GradeAttendanceForm(forms.ModelForm):
    class Meta:
        choices = (
        (5, 'отлично'),
        (4, 'хорошо'),
        (3, 'удовл.'),
        (2, 'неудовл.'),
        )
        model = Control_work_grade
        fields = ['grade'] # выбираются поля для формы
        widgets = {
            'grade': forms.RadioSelect(attrs={'class':''}, choices=choices),
        }


'''зачет/незачет'''
class GradeAttendanceFormOffset(forms.ModelForm):
    class Meta:
        choices = (
        (2, 'зачет'),
        (0, 'незачет'),
        )
        model = Control_work_grade
        fields = ['grade'] # выбираются поля для формы
        widgets = {
            'grade': forms.RadioSelect(attrs={'class':''}, choices=choices),
        }


'''100-(или n-) балльная шкала'''
class GradeAttendanceFormNPoint(forms.ModelForm):
    class Meta:
        model = Control_work_grade
        fields = ['grade'] # выбираются поля для формы
        widgets = {
            'grade': forms.NumberInput(attrs={'class':'input_attendance', 'min': 0,}),
        }
    
    def __init__(self, max_value, *args, **kwargs):
        super(GradeAttendanceFormNPoint, self).__init__(*args, **kwargs)
        self.fields['grade'].widget = forms.NumberInput(attrs={
            'class':'input_attendance', 
            'min': 0,
            'max': max_value,
            })



'''5-балльная шкала - select'''
class TeleWorkGradeForm(forms.ModelForm):
    class Meta:
        choices = (
        (5, 'отлично'),
        (4, 'хорошо'),
        (3, 'удовл.'),
        (2, 'неудовл.'),
        )
        model = TeleWork
        fields = ['grade', 'additional_comment'] # выбираются поля для формы
        widgets = {
            'grade': forms.Select(attrs={'class':'grades_select'}, choices=choices),
        }


'''зачет/незачет'''
class TeleWorkGradeFormOffset(forms.ModelForm):
    class Meta:
        choices = (
        (1, 'зачет'),
        (0, 'незачет'),
        )
        model = TeleWork
        fields = ['grade', 'additional_comment'] # выбираются поля для формы
        widgets = {
            'grade': forms.Select(attrs={'class':'grades_select'}, choices=choices),
        }


'''100-(или n-) балльная шкала'''
class TeleWorkGradeFormNPoint(forms.ModelForm):
    class Meta:
        model = TeleWork
        fields = ['grade', 'additional_comment'] # выбираются поля для формы
        widgets = {
            'grade': forms.NumberInput(attrs={
                'class':'input_attendance', 
                'min': 0,
                'data-class': '',
                }),
        }


'''5-балльная шкала - критерий'''
class GradeCriterionForm(forms.ModelForm):
    class Meta:
        choices = (
        (5, 'отлично'),
        (4, 'хорошо'),
        (3, 'удовл.'),
        (2, 'неудовл.'),
        )
        model = TeleWorkCriterions
        fields = ['grade'] # выбираются поля для формы
        widgets = {
            'grade': forms.Select(attrs={
                'class':'grades_select', 
                'data-class': '',
                }, choices=choices),
        }


'''5-балльная шкала - критерий - readonly'''
class GradeCriterionFormReadonly(forms.ModelForm):
    class Meta:
        choices = (
        (5, 'отлично'),
        (4, 'хорошо'),
        (3, 'удовл.'),
        (2, 'неудовл.'),
        )
        model = TeleWorkCriterions
        fields = ['grade'] # выбираются поля для формы
        widgets = {
            'grade': forms.Select(attrs={
                'class':'grades_select', 
                'data-class': '',
                'disabled': 'disabled'
                }, choices=choices),
        }


'''зачет/незачет - критерий'''
class GradeCriterionFormOffset(forms.ModelForm):
    class Meta:
        choices = (
        (1, 'Зачет'),
        (0, 'Незачет'),
        )
        model = TeleWorkCriterions
        fields = ['grade'] # выбираются поля для формы
        widgets = {
            'grade': forms.RadioSelect(
                attrs={'class':''}, 
                choices=choices,
                ),
        }
        

'''зачет/незачет - критерий - readonly'''
class GradeCriterionFormOffsetReadonly(forms.ModelForm):
    class Meta:
        choices = (
        (2, 'Зачет'),
        (0, 'Незачет'),
        )
        model = TeleWorkCriterions
        fields = ['grade'] # выбираются поля для формы
        widgets = {
            'grade': forms.RadioSelect(
                attrs={'class':'', 'disabled': 'disabled'}, 
                choices=choices,
                ),
        }


'''100-(или n-) балльная шкала - критерий'''
class GradeCriterionFormNPoint(forms.ModelForm):
    class Meta:
        model = TeleWorkCriterions
        fields = ['grade'] # выбираются поля для формы
        widgets = {
            'grade': forms.NumberInput(attrs={'class':'input_attendance', 'min': 0,}),
        }
    def __init__(self, max_value, *args, **kwargs):
        super(GradeCriterionFormNPoint, self).__init__(*args, **kwargs)
        self.fields['grade'].widget = forms.NumberInput(attrs={
            'class':'input_attendance', 
            'data-class': '',
            'min': 0,
            'max': max_value,
            })

'''100-(или n-) балльная шкала - критерий - readonly'''
class GradeCriterionFormNPointReadonly(forms.ModelForm):
    class Meta:
        model = TeleWorkCriterions
        fields = ['grade'] # выбираются поля для формы
        widgets = {
            'grade': forms.NumberInput(attrs={'class':'input_attendance', 'min': 0,}),
        }
    def __init__(self, max_value, *args, **kwargs):
        super(GradeCriterionFormNPointReadonly, self).__init__(*args, **kwargs)
        self.fields['grade'].widget = forms.NumberInput(attrs={
            'class':'input_attendance', 
            'data-class': '',
            'min': 0,
            'max': max_value,
            'readonly': 'readonly',
            })

class TeleWorkCriterionsCommentForm(forms.ModelForm):
    class Meta:
        choices = (
            ('', '----'),
            ('Расстановка скобок', 'Расстановка скобок'),
            )
        model = TeleWorkCriterionsComment
        fields = ['text', 'comment_type', 'teleworkcriterion'] # выбираются поля для формы
        widgets = {
            'text': forms.Textarea(),
            'comment_type': forms.Select(
                choices=choices,
                ),
            'teleworkcriterion': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(TeleWorkCriterionsCommentForm, self).__init__(*args, **kwargs)
        self.fields['text'].label = 'Замечание'
        self.fields['comment_type'].label = 'Типовое замечание'


'''Форма аттестации'''
class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ['schedule', 'number', 'name', 'type'] # выбираются поля для формы
        widgets = {
            'schedule': forms.HiddenInput(),
            'number': forms.NumberInput(),
            'name': forms.Textarea(),
            'type': forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        super(CertificationForm, self).__init__(*args, **kwargs)
        self.fields['number'].label = 'Номер аттестации'
        self.fields['name'].label = 'Название аттестации'
        self.fields['type'].label = 'Вид аттестации'


'''Форма способа выставления аттестации'''
class CertificationScaleBoolForm(ControlTypeScaleTranslate):
    PREDEFINDED_TRANSLATE_OPTIONS= (
        (None, 'Изначально по 5-балльной шкале'),
        (ControlTypeScaleTranslate.FROM_N_TO_FIVE, 'По 100-балльной шкале, с переводом в 5-балльную'),
    )

    def __init__(self, *args, **kwargs):
        super(CertificationScaleBoolForm, self).__init__(*args, **kwargs)
        self.fields['is_translate'].label = 'Способ выставления аттестации (укажите для каждой оценки максимальный балл)'


# '''Форма способа выставления аттестации'''
# class CertificationJobForm(forms.Form):
#     is_choosed = forms.BooleanField(
#         label='Выбрана ли работа', 
#         ) # без choices не работает (не указаны допустимые значения)
#     weight = forms.
    
#     def __init__(self, *args, **kwargs):
#         super(CertificationJobForm, self).__init__(*args, **kwargs)


'''Форма способа выставления аттестации'''
class CertificationJobForm(forms.ModelForm):
    is_choosed = forms.BooleanField()
    class Meta:
        model = Certification_control_work
        fields = ['weight', 'control_work'] # выбираются поля для формы
        widgets = {
            'control_work': forms.HiddenInput(),
            'weight': forms.NumberInput(attrs={
                'min': 0,
            }),
        }

    def __init__(self, *args, **kwargs):
        super(CertificationJobForm, self).__init__(*args, **kwargs) 
        self.fields['is_choosed'].widget.attrs['class'] = 'is_choosed_checkbox'


'''Оценка в пятибалльной шкале'''
class CertificationGradeForm(forms.ModelForm):
    class Meta:
        choices = (
            (5, 'отлично'),
            (4, 'хорошо'),
            (3, 'удовл.'),
            (2, 'неудовл.'),
            )
        model = Certification_control_work_grade
        fields = ['certification', 'student', 'grade'] # выбираются поля для формы
        widgets = {
            'certification': forms.HiddenInput(),
            'student': forms.HiddenInput(),
            'grade': forms.Select(attrs={
                'class':'grades_select', 
                'data-class': '',
                }, choices=choices),
        }


'''Оценка в стобалльной шкале'''
class CertificationGradeFormPoints(forms.ModelForm):
    class Meta:
        model = Certification_control_work_grade
        fields = ['grade', 'certification', 'student'] # выбираются поля для формы
        widgets = {
            'certification': forms.HiddenInput(),
            'student': forms.HiddenInput(),
            'grade': forms.NumberInput(
                attrs={
                    'class':'input_attendance', 
                    'data-class': '',
                    'min': 0,
                    'max': 100,
                    }),
        }