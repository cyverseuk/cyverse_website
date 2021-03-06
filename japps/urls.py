from django.conf.urls import url
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from django.urls import reverse_lazy

from . import views

app_name="japps"
urlpatterns = [
    #url(r'^$', views.IndexView.as_view(), name="index"),
    url(r'^$',views.list_apps,name='index'),
    # ex: /japps/submission.html/
    url(r'^submission/$', RedirectView.as_view(url=reverse_lazy('japps:index')), name='go-to-index'),
    url(r'^submission/(?P<application>[\.\w-]+)$', views.create_form, name='submission'),
    url(r'^contact/$', views.contact, name='contact'),
    url(r'^job_submitted/$', views.submitted, name='job_submitted' ),
    url(r'^applications/$', views.applications, name='applications'),
    url(r'^applications/(?P<app_name>[\.\w-]+)$', views.app_description, name='app_description'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^archive/$', views.archive, name='archive'),
]
