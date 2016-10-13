from django.views import generic
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from .forms import ApplicationForm

def get_name(request):
    if request.method=='POST':
        form=ApplicationForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/job_submitted/')
    else:
        form=ApplicationForm()
    return render(request, 'japps/submission.html', {'form': form})
