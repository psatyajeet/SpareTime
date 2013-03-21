from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import HttpResponse, HttpResponseNotFound
import calendar
from datetime import date, timedelta, datetime
from dateutil import tz
from django.utils import simplejson

from socialcalendar.models import Event


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
        dateString = "%m/%d/%Y %I:%M %p"
        startDate = datetime.strptime(request.POST['startTime'],
                                          dateString)
        endDate = datetime.strptime(request.POST['endTime'],
                                          dateString)

        startDate = startDate.replace(tzinfo=tz.gettz('UTC'))
        endDate = endDate.replace(tzinfo=tz.gettz('UTC'))
        startDate = startDate.astimezone(tz.tzlocal())
        endDate = endDate.astimezone(tz.tzlocal())

        e = Event(
            title=request.POST['title'],
            description=request.POST['description'],
            location=request.POST['location'],
            start=startDate,
            end=endDate,
        )

        e.save()
        #d = {'header': header, 'days': days, 'dates': dates}
        return HttpResponse()
    else:
        return HttpResponseNotFound()


@csrf_protect
def populateEvents(request):
    today = date.today() + timedelta(request.session['whichweek']*7)
    delta = timedelta((today.weekday()+1) % 7)
    first = today - delta
    last = first + timedelta(7)

    events = Event.objects.filter(start__gte=first).filter(end__lt=last)
    d = []
    for e in events:
        d.append({
            'title': e.title,
            'start': e.start.hour+e.start.minute/60.0,
            'end': e.end.hour+e.end.minute/60.0,
            'day': ((e.start.weekday()+1) % 7),
        })

    return HttpResponse(simplejson.dumps(d))
