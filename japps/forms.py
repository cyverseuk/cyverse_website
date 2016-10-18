import json

from django import forms
from django.forms import ModelForm
from . import models

class NameJob(forms.Form):
    name_job=forms.CharField(label="Job Name", max_length=50, required=True)

class ParameterForm(forms.Form):

    def __init__(self, *args, **kwargs) :
        super(ParameterForm,self).__init__(*args,**kwargs)
