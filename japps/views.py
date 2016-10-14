import os
import json

from django.views import generic
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.conf import settings

from .forms import ApplicationForm, NameJob, NumericalForm, BooleanForm, TextForm

a=open(os.path.join(settings.PROJECT_ROOT, 'MikadoApp.json'))
ex_json=json.load(a)

def get_name(request):
    if request.method=='POST':
        form=ApplicationForm(request.POST)
        name_form=NameJob(request.POST, initial={"name_job":ex_json["name"]})
        num_form=NumericalForm(request.POST)
        bool_form=BooleanForm(request.POST)
        text_form=TextForm(request.POST)
        if form.is_valid() and name_form.is_valid() and num_form.is_valid() and bool_form.is_valid() and text_form.is_valid():
            return HttpResponseRedirect('/job_submitted/')
    else:
        form=ApplicationForm()
        name_form=NameJob(initial={"name_job":ex_json["name"]})
        num_form=NumericalForm()
        bool_form=BooleanForm()
        text_form=TextForm()
    return render(request, 'japps/submission.html', {'form': form, 'json_app': ex_json, 'name_form': name_form, 'num_form': num_form, "bool_form": bool_form, "text_form": text_form } )
