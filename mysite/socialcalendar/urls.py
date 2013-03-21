from django.conf.urls import patterns, url

from socialcalendar import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^ajax', views.ajax, name='ajax'),
)
