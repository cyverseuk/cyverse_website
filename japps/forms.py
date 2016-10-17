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

class ParameterForm(forms.Form):

    def __init__(self, **kwargs) :
        super(ParameterForm,self).__init__(**kwargs)
        namefield=kwargs.get("valuename")
        #should never be undefined
        if valuename==None or kwargs.get("parameter_type")==None:
            return "error"
        if kwargs["parameter_type"]=="string":
            self.fields[namefield]=forms.CharField(max_length=50)
            self.fields[namefield].label=kwargs.get("parameter_label", namefield)
            self.fields[namefield].help_text=kwargs.get("parameter_description", "") ###note this may be empty
            #self.fields["value"].default=parameter_default ###note this may be empty as well
            #if parameter_regex!="": ###synthax? -set it as default if not given--
            #    self.fields["value"].validators=parameter_regex
            #else:
            #    pass #leaving this here as it may give errors?
        elif kwargs["parameter_type"]=="number":
            self.fields[namefield]=forms.FloatField(label=kwargs.get("parameter_label", namefield))
            self.fields[namefield].help_text=kwargs.get("parameter_description", "")
            #if parameter_regex!="":
            #    value=forms.FloatField(label=parameter_label, validators=parameter_regex)
            #else:
            #    value=forms.FloatField(label=parameter_label, validators=parameter_regex)
        elif kwargs["parameter_type"]=="bool" or kwargs["parameter_type"]=="flag":
            self.fields[namefield]=forms.BooleanField(label=kwargs.get("parameter_label", namefield))
            self.fields[namefield].help_text=kwargs.get("parameter_description", "")
        else:
            #should never be here as agave validate the json
            return "error: parameter type not valid."
