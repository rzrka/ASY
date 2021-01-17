from django import forms
from django.core.exceptions import ValidationError

from mainapp.models import *


'''зачет/незачет'''
class JobHistoryCommentForm(forms.ModelForm):
    class Meta:
        model = TeleWork
        fields = ['additional_comment_student'] # выбираются поля для формы
        widgets = {

        }


'''Telework - student comment'''
class TeleWorkCriterionsCommentForm(forms.ModelForm):
    class Meta:
        model = TeleWorkCriterionsCommentStudent
        fields = ['text', 'teleworkcriterion'] # выбираются поля для формы
        widgets = {
            'text': forms.Textarea(),
            'teleworkcriterion': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(TeleWorkCriterionsCommentForm, self).__init__(*args, **kwargs)
        self.fields['text'].label = 'Замечание'