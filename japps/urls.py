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
    url(r'^job_submitted/$', views.submitted, name='job_submitted' ),
]
