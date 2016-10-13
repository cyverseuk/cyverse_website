from django import forms

class ApplicationForm(forms.Form):
    job_name=forms.CharField(label="Job name", max_length=100)
