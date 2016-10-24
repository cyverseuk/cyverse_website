import os
import json
from collections import OrderedDict
import requests
import urllib3.contrib.pyopenssl
import certifi
import urllib3

from django import forms
from django.views import generic
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.core.validators import RegexValidator
from django import forms

from .forms import ParameterForm

a=open(os.path.join(settings.PROJECT_ROOT, 'KallistoApp.json'))
ex_json=json.load(a)
nameapp=ex_json["name"]
a.close()
with open(os.path.join(settings.PROJECT_ROOT, 'token.txt')) as b:
    token=next(b).strip()
urllib3.contrib.pyopenssl.inject_into_urllib3()
http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

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
        nice_form=forms.Form(request.POST, request.FILES)
        if nice_form.is_valid():
            """
            if the form is valid the user is addressed to the
            following page.
            """
            json_data=nice_form.cleaned_data
            return HttpResponseRedirect('/japps/job_submitted/', request.POST)

    else:
        """
        dynamically create a form accordingly to the json file
        """
        fields=OrderedDict()
        fields["name_job"]=forms.CharField(initial=ex_json["name"]+"-"+str(timezone.now().date())+"-"+str(timezone.now().strftime('%H:%M:%S')))
        for field in ex_json["inputs"]:
            #####
            #ideally here i want to have mutually exclusive options for the user to give URL for the file or to upload the file. additional problem with the url option is that apparently the widget doens't have an option to allows multiple entries.
            #####
            if field.get("semantics")!=None:
                if field["semantics"].get("maxCardinality")>1 or field["semantics"].get("maxCardinality")==-1:
                    fields[field["id"]]=forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
                    #fields[field["id"]]=forms.URLField()
                else:
                    fields[field["id"]]=forms.FileField()
                    #fields[field["id"]]=forms.URLField()
            else:
                fields[field["id"]]=forms.FileField()
                #fields[field["id"]]=forms.URLField()
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
                    choices=[]
                    for pos in field["value"]["enumValues"]:
                        choices.append((pos,pos))
                    fields[field["id"]]=forms.ChoiceField(choices=choices)
            additional_features(field)
        nice_form=type('forms.Form', (forms.BaseForm,), {'base_fields': fields})
    return render(request, 'japps/submission.html', { "title": nameapp, "description": ex_json["longDescription"], "nice_form": nice_form } )

def create_json_run(request):
    json_run={}
    json_run["name"]=request.POST["name_job"]
    json_run["appId"]=ex_json["name"]+"-"+ex_json["version"]
    json_run["inputs"]={}
    json_run["parameters"]={}
    json_run["archive"]=False
    for field in request.POST:
        if field!="csrfmiddlewaretoken" and field!="name_job":
            if request.POST.get(field) not in [None, ""]:
                json_run["parameters"][field]=request.POST.get(field)
    for field in request.FILES:
        json_run["inputs"][field]=request.FILES[field].name
        header={"Authorization": "Bearer "+token}
        for fie in request.FILES.getlist(field):
            ####check synthax for file= and fix the upload part for the field in the form
            requests.post("https://agave.iplantc.org/files/v2/media/system/cyverseUK-Storage2/temp/?pretty=true", files={"fileToUpload": (fie.name, fie.read())}, headers=header)
    json_run=json.dumps(json_run)
    header={"Authorization": "Bearer "+token, 'Content-Type': 'application/json'}
    r=requests.post("https://agave.iplantc.org/jobs/v2/?pretty=true", data=json_run, headers=header)
    return render(request, "japps/job_submitted.html", {"json_run": json_run, "risposta": r.text, "codice": r.status_code, "t": token, "headers": r.request.headers})
