from django.conf.urls import url

from . import views

app_name="japps"
urlpatterns = [
    #url(r'^$', views.IndexView.as_view(), name="index"),
    # ex: /japps/submission.html/
    url(r'^submission/$', views.get_name, name='submission'),
]
