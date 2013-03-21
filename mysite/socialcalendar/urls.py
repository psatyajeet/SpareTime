from django.conf.urls import patterns, url

from socialcalendar import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^changeWeek', views.changeWeek, name='changeWeek'),
    url(r'^submitEvent', views.submitEvent, name='submitEvent'),
    url(r'^populateEvents', views.populateEvents, name='populateEvents'),
)
