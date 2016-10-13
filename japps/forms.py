import json

from django import forms
from . import models

class ApplicationForm(forms.Form):
    job_name=forms.CharField(label="Job name", max_length=100, required=True)

    class Meta:
        model=models.Application
