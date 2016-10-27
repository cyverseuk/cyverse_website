from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

app_name="japps"
urlpatterns = [
    #url(r'^$', views.IndexView.as_view(), name="index"),
    url(r'^$',views.list_apps,name='index'),
    # ex: /japps/submission.html/
    url(r'^submission/$', views.create_form, name='submission'),
    url(r'^job_submitted/$', views.create_json_run, name='job_submitted' ),
]
