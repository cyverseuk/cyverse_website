from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

app_name="japps"
urlpatterns = [
    #url(r'^$', views.IndexView.as_view(), name="index"),
    url(r'^$',
    TemplateView.as_view(template_name='japps/index.html'),
    name='index'),
    # ex: /japps/submission.html/
    url(r'^submission/$', views.get_name, name='submission'),
]
