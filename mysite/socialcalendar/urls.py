from django.conf.urls import patterns, url

from socialcalendar import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^changeWeek', views.changeWeek, name='changeWeek'),
    url(r'^goToEvent', views.goToEvent, name='goToEvent'),
    url(r'^submitEvent', views.submitEvent, name='submitEvent'),
    url(r'^populateEvents', views.populateEvents, name='populateEvents'),
    url(r'^getEventData', views.getEventData, name='getEventData'),
    url(r'^deleteEvent', views.deleteEvent, name='deleteEvent'),
    url(r'^editEvent', views.editEvent, name='editEvent'),
    url(r'^changeStart', views.changeStart, name='changeStart'),
    url(r'^gcal', views.gcal, name='gcal'),
    url(r'^comment', views.comment, name='comment'),
    url(r'^getComments', views.getComments, name='getComments'),

    url(r'^addFriendsToEvent', views.addFriendsToEvent, name='addFriendsToEvent'),
    url(r'^addCreatorsToEvent', views.addCreatorsToEvent, name='addCreatorsToEvent'),

    url(r'^rejectNotification', views.rejectNotification, name='rejectNotification'),
    url(r'^acceptNotification', views.acceptNotification, name='acceptNotification'),

    url(r'^getNotificationsRequest', views.getNotificationsRequest, name='getNotificationsRequest'),

    url(r'^deleteCookie', views.deleteCookie, name='deleteCookie'),

    url(r'^makeUser', views.makeUser, name='makeUser'),
    url(r'^getPeople', views.getPeople, name='getPeople'),

    url(r'^changeFormat', views.changeFormat, name='changeFormat'),
    url(r'^changeMonth', views.changeMonth, name='changeMonth'),
    url(r'^populateMonthEvents', views.populateMonthEvents, name='populateMonthEvents'),
    url(r'^heatMap', views.heatMap, name='heatMap'),
    url(r'^addName', views.addName, name='addName'),
)
