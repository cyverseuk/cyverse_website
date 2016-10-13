import os
import json

from django.views import generic
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.conf import settings

from .forms import ApplicationForm

a=open(os.path.join(settings.PROJECT_ROOT, 'GWasserApp.json'))
ex_json=json.load(a)

def get_name(request):
    if request.method=='POST':
        form=ApplicationForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/job_submitted/')
    else:
        form=ApplicationForm()
    return render(request, 'japps/submission.html', {'form': form, 'json_app': ex_json} )
