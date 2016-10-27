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

def create_form(request, application):
    global fields
    global job_time
    header={"Authorization": "Bearer "+token}
    r=requests.get("https://agave.iplantc.org/apps/v2/"+application+"?pretty=true", headers=header)
    ex_json=r.json()
    nameapp=ex_json["result"]["name"]
    job_time=str(timezone.now().date())+"-"+str(timezone.now().strftime('%H%M%S'))
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
        fields["name_job"]=forms.CharField(initial=ex_json["result"]["name"]+"-"+job_time)
        for field in ex_json["result"]["inputs"]:
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
        for field in ex_json["result"]["parameters"]:
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
                    for pos in field["value"]["enum_values"]:
                        choices.append((pos,pos))
                    fields[field["id"]]=forms.ChoiceField(choices=choices)
            additional_features(field)
        nice_form=type('forms.Form', (forms.BaseForm,), {'base_fields': fields})
    return render(request, 'japps/submission.html', { "title": nameapp, "description": ex_json["result"]["longDescription"], "nice_form": nice_form } )

def create_json_run(request):
    global job_time
    job_time=str(timezone.now().date())+"-"+str(timezone.now().strftime('%H%M%S'))
    json_run={}
    json_run["name"]=request.POST["name_job"]
    json_run["appId"]=ex_json["name"]+"-"+ex_json["version"]
    json_run["inputs"]={}
    json_run["parameters"]={}
    json_run["archive"]=False
    header={"Authorization": "Bearer "+token}
    for field in request.POST:
        if field!="csrfmiddlewaretoken" and field!="name_job":
            if request.POST.get(field) not in [None, ""]:
                json_run["parameters"][field]=request.POST.get(field)
    if len(request.FILES)>0:
        requests.put("https://agave.iplantc.org/files/v2/media/system/cyverseUK-Storage2/temp/?pretty=true", data={"action":"mkdir","path":job_time}, headers=header)
    for field in request.FILES:
        json_run["inputs"][field]=[]
        for fie in request.FILES.getlist(field):
            json_run["inputs"][field].append("agave://cyverseUK-Storage2//mnt/data/temp/"+job_time+"/"+fie.name)
            ####check synthax for file= and fix the upload part for the field in the form
            rr=requests.post("https://agave.iplantc.org/files/v2/media/system/cyverseUK-Storage2/temp/"+job_time+"/?pretty=true", files={"fileToUpload": (fie.name, fie.read())}, headers=header)
            #print rr.text
            #print rr.status_code
            #print rr.request.headers
    json_run=json.dumps(json_run)
    header={"Authorization": "Bearer "+token, 'Content-Type': 'application/json'}
    r=requests.post("https://agave.iplantc.org/jobs/v2/?pretty=true", data=json_run, headers=header)
    #requests.delete("https://agave.iplantc.org/files/v2/media/system/cyverseUK-Storage2/temp/"+job_time, headers=header)
    return render(request, "japps/job_submitted.html", {"json_run": json_run, "risposta": r.text, "codice": r.status_code, "t": token, "headers": r.request.headers})

def list_apps(request):
    """
    this function will retrieve the apps available on our system
    cyverseUK-Batch2 and create a list with their names and version. each of
    the item list will be a link calling the create_form() function for that
    specific application.
    """
    header={"Authorization": "Bearer "+token}
    r=requests.get("https://agave.iplantc.org/apps/v2?publicOnly=true&executionSystem.eq=cyverseUK-Batch2&pretty=true", headers=header)
    display_list=[]
    risposta=r.json()
    for el in risposta["result"]:
        display_list.append(el["id"])
    return render(request, "japps/index.html", {"risposta": display_list})
