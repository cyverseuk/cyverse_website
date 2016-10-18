import os
import json
from collections import OrderedDict

from django import forms
from django.views import generic
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.core.validators import RegexValidator

from .forms import ParameterForm

a=open(os.path.join(settings.PROJECT_ROOT, 'GWasserApp.json'))
ex_json=json.load(a)
nameapp=ex_json["name"]

def additional_features(field):
    global fields
    fields[field["id"]].label=field["details"].get("label", field["id"])
    fields[field["id"]].help_text=field["details"].get("description", "")
    if field["value"].get("default",None) is not None:
        fields[field["id"]].initial=field["value"]["default"]
    if field["value"].get("validator", None) is not None:
        my_validator=RegexValidator(regex=field["value"]["validator"], message="Enter a valid value.")
        fields[field["id"]].validators=[my_validator]
    if field["value"].get("required")!=True:
        fields[field["id"]].required=False

def create_form(request):
    global fields
    if request.method=='POST':
        """
        form is filled in
        """
        nice_form=ParameterForm(request.POST)
        if nice_form.is_valid():
            """
            if the form is valid the user is addressed to the
            following page.
            """
            return HttpResponseRedirect('/japps/job_submitted/', request.POST)

    else:
        """
        dynamically create a form accordingly to the json file
        """
        fields=OrderedDict()
        fields["name_job"]=forms.CharField(initial=ex_json["name"]+"-"+str(timezone.now().date())+"-"+str(timezone.now().strftime('%H:%M:%S')))
        for field in ex_json["inputs"]:
            if field.get("semantics")!=None:
                if field["semantics"].get("maxCardinality")>1 or field["semantics"].get("maxCardinality")==-1:
                    fields[field["id"]]=forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
                else:
                    fields[field["id"]]=forms.FileField()
            else:
                fields[field["id"]]=forms.FileField()
            additional_features(field)
        for field in ex_json["parameters"]:
            if field["value"].get("type")==None:
                return "error" #should nver be here as this check is done by agave
            else:
                if field["value"]["type"]=="string":
                    fields[field["id"]]=forms.CharField(max_length=50)
                elif field["value"]["type"]=="number":
                    fields[field["id"]]=forms.FloatField()
                elif field["value"]["type"]=="bool" or field["value"]["type"]=="flag":
                    fields[field["id"]]=forms.BooleanField()
                elif field["value"]["type"]=="enumeration":
                    fields[field["id"]]=forms.ChoiceField(choices=enumerate(field["value"]["enumValues"]))
            additional_features(field)
        nice_form=type('ParameterForm', (forms.BaseForm,), {'base_fields': fields})
    return render(request, 'japps/submission.html', { "title": nameapp, "nice_form": nice_form } )

def create_json_run(filled_form):
    data={}
    data["name"]=nameapp
    data["appId"]=ex_json["version"]
    data["archive"]=True
    data["inputs"]=[]
    data["parameters"]=[]
    json_data=json.dumps(data)
    return render(filled_form, "japps/job_submitted.html", {"json_data":json_data})
