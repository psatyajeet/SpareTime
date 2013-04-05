import httplib2
import sys

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run

from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import HttpResponse, HttpResponseNotFound
import calendar
from datetime import date, timedelta, datetime
from dateutil import tz
from django.utils import simplejson

from socialcalendar.models import Event


dateString = "%m/%d/%Y %I:%M %p"


def getDays(offset=0):
    calendar.setfirstweekday(calendar.SUNDAY)
    # Days contains the abbrevations for the days of the week

    today = date.today() + timedelta(offset*7)
    delta = timedelta((today.weekday()+1) % 7)
    first = today - delta
    delta = timedelta(1)

    days = []
    for i in range(6, 13):
        isToday = (offset == 0 and (i % 7) == ((today.weekday()) % 7))
        days.append({"title": calendar.day_abbr[i % 7],
                     "today": isToday})

    year = first.strftime("%Y")
    month = first.strftime("%B")
    day = first.strftime("%d").lstrip("0")

    last = first + timedelta(6)

    header = month + " " + day
    if (year != last.strftime("%Y")):
        header += ", " + year
    header += " - "

    if (month != last.strftime("%B")):
        header += " " + last.strftime("%B") + " "

    header += last.strftime("%d").lstrip("0") + ", " + last.strftime("%Y")

    dates = []
    for i in range(7):
        dates.append({"year": (first.year),
                      "month": (first.month-1),
                      "day": (first.day)})

        days[i]['title'] += " "+first.strftime("%m/").lstrip("0") + \
            first.strftime("%d").lstrip("0")

        first = first + delta

    hour = 12
    hours = []

    for i in range(24):
        string = str(hour)
        if (i < 12):
            string = string + " AM"
        else:
            string = string + " PM"
        hours.append(string)
        if hour == 12:
            hour = 1
        else:
            hour = hour + 1

    return days, hours, dates, header


@ensure_csrf_cookie
def index(request):

    if (not request.session.__contains__('whichweek')):
        request.session['whichweek'] = 0

    days, hours, dates, header = getDays(request.session['whichweek'])
    context = {
        'days': days,
        'hours': hours,
        'dates': dates,
        'header': header,
        'events': Event.objects.all(),
    }

    return render(request, 'socialcalendar/calendar.html', context)


@csrf_protect
def changeWeek(request):
    if request.method == "POST":
        change = int(request.POST['amount'])
        if (change == 0):
            request.session['whichweek'] = 0
        else:
            request.session['whichweek'] += change
        days, hours, dates, header = getDays(request.session['whichweek'])
        d = {'header': header, 'days': days, 'dates': dates}
        return HttpResponse(simplejson.dumps(d))
    else:
        return HttpResponseNotFound()


@csrf_protect
def submitEvent(request):
    if request.method == "POST":
        startDate = datetime.strptime(request.POST['startTime'],
                                      dateString)
        endDate = datetime.strptime(request.POST['endTime'],
                                    dateString)
        startDate = startDate.replace(tzinfo=tz.gettz('UTC'))
        endDate = endDate.replace(tzinfo=tz.gettz('UTC'))
        startDate = startDate.astimezone(tz.gettz('UTC'))
        endDate = endDate.astimezone(tz.gettz('UTC'))
        
        e = Event(
            title=request.POST['title'],
            description=request.POST['description'],
            location=request.POST['location'],
            start=startDate,
            end=endDate,
            gid=''
        )

        e.save()
        #d = {'header': header, 'days': days, 'dates': dates}
        return HttpResponse()
    else:
        return HttpResponseNotFound()


@csrf_protect
def populateEvents(request):
    today = datetime.today() + timedelta(request.session['whichweek']*7)
    today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    delta = timedelta((today.weekday()+1) % 7)
    first = today - delta
    last = first + timedelta(7)

    first = first.replace(tzinfo=tz.gettz('UTC'))
    last = last.replace(tzinfo=tz.gettz('UTC'))

    events = Event.objects.filter(start__gte=first).filter(end__lt=last)
    events = events.extra(order_by=['start'])
    d = []
    if (len(events) == 0):
        return HttpResponse(simplejson.dumps(d))
    x = 0
    last = 0
    biggestEnd = events[0].end
    widths = []
    xs = []
    for i in range(len(events)-1):
        xs.append(x)
        if events[i].end > biggestEnd:
            biggestEnd = events[i].end
        if biggestEnd > events[i+1].start:
            x = x + 1
        else:
            for j in range(last, i+1):
                widths.append(x+1)
            biggestEnd = events[i+1].end
            x = 0
            last = i+1

    xs.append(x)
    for j in range(last, len(events)):
        widths.append(x+1)

    for i in range(len(events)):
        e = events[i]
        d.append({
            'title': e.title,
            'start': e.start.hour+e.start.minute/60.0,
            'end': e.end.hour+e.end.minute/60.0,
            'day': ((e.start.weekday()+1) % 7),
            'id': e.id,
            'x': xs[i]/float(widths[i]),
            'width': 1.0/float(widths[i]),
        })

    return HttpResponse(simplejson.dumps(d))


@csrf_protect
def getEventData(request):

    if request.method == "POST":
        events = Event.objects.filter(id=request.POST['id'])
        if (len(events) != 1):
            return HttpResponseNotFound()
        else:
            event = list(events)[0]
            d = {
                'title': event.title,
                'description': event.description,
                'location': event.location,
                'start': event.start.strftime(dateString),
                'end': event.end.strftime(dateString),
                'id': event.id,
            }
            return HttpResponse(simplejson.dumps(d))
    else:
        return HttpResponseNotFound()


@csrf_protect
def deleteEvent(request):

    if request.method == "POST":
        event = Event.objects.get(id=request.POST['id'])
        event.delete()
        return HttpResponse()
    else:
        return HttpResponseNotFound()


@csrf_protect
def editEvent(request):
    if request.method == "POST":
        event = Event.objects.get(id=request.POST['id'])
        startDate = datetime.strptime(request.POST['startTime'],
                                      dateString)
        endDate = datetime.strptime(request.POST['endTime'],
                                    dateString)

        startDate = startDate.replace(tzinfo=tz.gettz('UTC'))
        endDate = endDate.replace(tzinfo=tz.gettz('UTC'))
        startDate = startDate.astimezone(tz.tzlocal())
        endDate = endDate.astimezone(tz.tzlocal())

        event.title = request.POST['title']
        event.description = request.POST['description']
        event.location = request.POST['location']
        event.start = startDate
        event.end = endDate
        
        event.save()
        return HttpResponse()
    else:
        return HttpResponseNotFound()


@csrf_protect
def changeStart(request):
    if request.method == "POST":
        event = Event.objects.get(id=request.POST['id'])
        startDate = datetime.strptime(request.POST['startTime'],
                                      dateString)

        startDate = startDate.replace(tzinfo=tz.gettz('UTC'))
        startDate = startDate.astimezone(tz.tzlocal())

        eventLength = event.end - event.start
        event.start = startDate
        event.end = startDate + eventLength

        event.save()
        return HttpResponse()
    else:
        return HttpResponseNotFound()


@csrf_protect
def gcal(request):
    client_id = '984176055001-8kq2incml2fo37fb1l9e8spu0j3uk906.apps.googleusercontent.com'
    client_secret = 'UInVj9loCowEztBqN8EcCwZV'

    # The scope URL for read/write access to a user's calendar data
    scope = 'https://www.googleapis.com/auth/calendar'

    # Create a flow object. This object holds the client_id, client_secret, and
    # scope. It assists with OAuth 2.0 steps to get user authorization and
    # credentials.
    flow = OAuth2WebServerFlow(client_id, client_secret, scope, oauth_callback = 'http://localhost:8000', redirect_uri = 'http://localhost:8000')
    
    # Create a Storage object. This object holds the credentials that your
    # application needs to authorize access to the user's data. The name of the
    # credentials file is provided. If the file does not exist, it is
    # created. This object can only hold credentials for a single user, so
    # as-written, this script can only handle a single user.
    storage = Storage('credentials.dat')

    # The get() function returns the credentials for the Storage object. If no
    # credentials were found, None is returned.
    credentials = storage.get()

    # If no credentials are found or the credentials are invalid due to
    # expiration, new credentials need to be obtained from the authorization
    # server. The oauth2client.tools.run() function attempts to open an
    # authorization server page in your default web browser. The server
    # asks the user to grant your application access to the user's data.
    # If the user grants access, the run() function returns new credentials.
    # The new credentials are also stored in the supplied Storage object,
    # which updates the credentials.dat file.
    if credentials is None or credentials.invalid:
        credentials = run(flow, storage)
    # Create an httplib2.Http object to handle our HTTP requests, and authorize it
    # using the credentials.authorize() function.
    http = httplib2.Http()
    http = credentials.authorize(http)

    # The apiclient.discovery.build() function returns an instance of an API service
    # object can be used to make API calls. The object is constructed with
    # methods specific to the calendar API. The arguments provided are:
    #   name of the API ('calendar')
    #   version of the API you are using ('v3')
    #   authorized httplib2.Http() object that can be used for API calls
    service = build('calendar', 'v3', http=http)
    page_token = None

    while True:
        events = service.events().list(calendarId='primary').execute()
        if events['items']:
            for event in events['items']:
                existentEvent = Event.objects.filter(gid=event['iCalUID'])
                if(len(existentEvent) != 0):
                    continue
                if not event.has_key('summary'):
                    event['summary'] = ''
                if not event.has_key('description'):
                    event['description'] = ''
                if not event.has_key('location'):
                    event['location'] = ''
                if not event.has_key('start'):
                    event['start']['dateTime'] = ''
                if not event.has_key('end'):
                    event['end']['dateTime'] = ''
                if not event.has_key('iCalUID'):
                    event['iCalUID'] = ''
            
                e = Event(title=event['summary'],
                          description=event['description'],
                          location=event['location'],
                          start=event['start']['dateTime'].replace("T", " "),
                          end=event['end']['dateTime'].replace("T", " "),
                          gid=event['iCalUID']
                          )
                e.save()
        page_token = events.get('nextPageToken')
        if not page_token:
            break
    return HttpResponse()
