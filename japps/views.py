import os
import json
from collections import OrderedDict

from django import forms
from django.views import generic
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.conf import settings

from .forms import ParameterForm

a=open(os.path.join(settings.PROJECT_ROOT, 'MikadoApp.json'))
ex_json=json.load(a)

def additional_features(field):
    global fields
    fields[field["id"]].label=field["details"].get("label", field["id"])
    fields[field["id"]].help_text=field["details"].get("description", "")
    if field["value"].get("default")!=None:
        fields[field["id"]].default=field["value"].get("default")
    if field["value"].get("validator")!=None:
        fields[field["id"]].validators=field["value"].get("validator")
    if field["value"].get("required")!=True:
        fields[field["id"]].required=False

def get_name(request):
    global fields
    if request.method=='POST':
        nice_form=ParameterForm(request.POST)
        if nice_form.is_valid():
            return HttpResponseRedirect('/job_submitted/')
    else:
        fields=OrderedDict()
        fields["name_job"]=forms.CharField(initial=ex_json["name"])
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
    return render(request, 'japps/submission.html', { 'json_app': ex_json, "nice_form": nice_form } )
