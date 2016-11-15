from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

app_name="japps"
urlpatterns = [
    #url(r'^$', views.IndexView.as_view(), name="index"),
    url(r'^$',views.list_apps,name='index'),
    # ex: /japps/submission.html/
    url(r'^submission/$', views.list_apps),
    url(r'^submission/(?P<application>[\.\w-]+)$', views.create_form, name='submission'),
    url(r'^job_submitted/$', views.submitted, name='job_submitted' ),
]
