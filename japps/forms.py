import json

from django import forms
from django.forms import ModelForm
from . import models

class NameJob(forms.Form):
    name_job=forms.CharField(label="Job Name", max_length=50, required=True)

class ApplicationForm(ModelForm):
    value=forms.CharField(label="")

    class Meta:
        model=models.Input
        fields="__all__"

class NumericalForm(ModelForm):
    value=forms.FloatField(label="")

    class Meta:
        model=models.NumericalParameter
        fields="__all__"

class BooleanForm(ModelForm):
    value=forms.BooleanField(label="")

    class Meta:
        model=models.BooleanParameter
        fields="__all__"

class TextForm(ModelForm):
    value=forms.CharField(label="")

    class Meta:
        model=models.TextParameter
        fields="__all__"
