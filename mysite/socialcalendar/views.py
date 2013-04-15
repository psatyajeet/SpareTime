from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
import calendar
from datetime import date, timedelta, datetime
import time
from dateutil import tz
from django.utils import simplejson
from dateutil.relativedelta import relativedelta

from socialcalendar.models import Event
from socialcalendar.models import UserProfile

import json  

import random

dateString = "%m/%d/%Y %I:%M %p"
googleDateString = "%Y-%m-%dT%H:%M:%S"


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


def getWeeks(offset=0):
    calendar.setfirstweekday(calendar.SUNDAY)
    # Days contains the abbrevations for the days of the week

    today = date.today()
    current = date.today() + relativedelta(months=offset)
    first, monthrange = calendar.monthrange(current.year, current.month)
    first = (first+1) % 7
    previousMonth = current + relativedelta(months=-1)
    hold, previousMonthrange = calendar.monthrange(previousMonth.year, previousMonth.month)

    days = []
    for i in range(6, 13):
        days.append({"title": calendar.day_abbr[i % 7]})

    header = current.strftime("%B %Y")

    dates = []
    weeks = []
    for i in range(first):
        isToday = False
        if (today.year == previousMonth.year and
           today.month == previousMonth.month and
           today.day == previousMonthrange+i-first):

            isToday = True

        dates.append({"date": previousMonthrange+i-first+1,
                      "thisMonth": False,
                      "today": isToday})

    for i in range(first, monthrange+first):
        isToday = False
        if (current.year == today.year and
           current.month == today.month and
           i == current.day - first + 1):

            isToday = True
        dates.append({"date": i-first+1, "thisMonth": True, "today": isToday})
        if (i % 7 == 6):
            weeks.append(dates)
            dates = []

    nextMonth = (current + relativedelta(months=1))
    for i in range(monthrange+first+1, monthrange+first+8):
        isToday = False
        if (today.year == nextMonth.year and
           today.month == nextMonth.month and
           today.day == i - monthrange - first):

            isToday = True

        dates.append({"date": i - monthrange-first, "thisMonth": False, "today": isToday})
        if ((i-1) % 7 == 6):
            weeks.append(dates)
            break

    return days, weeks, header


@ensure_csrf_cookie
def index(request):

    if request.session.get('fbid')==None:
        return render(request, 'homepage.html')
        
    if (not request.session.__contains__('whichweek')):
        request.session['whichweek'] = 0

    if (not request.session.__contains__('whichmonth')):
        request.session['whichmonth'] = 0

    if (not request.session.__contains__('format')):
        request.session['format'] = "weekly"

    days, hours, dates, weekHeader = getDays(request.session['whichweek'])
    monthDays, monthWeeks, monthHeader = getWeeks(request.session['whichmonth'])

    if request.session['format'] == "weekly":
        header = weekHeader
    if request.session['format'] == "monthly":
        header = monthHeader

    context = {
        'format': request.session['format'],
        'days': days,
        'hours': hours,
        'dates': dates,
        'header': header,
        'events': Event.objects.all(),
        'monthDays': monthDays,
        'monthWeeks': monthWeeks,
    }

    return render(request, 'socialcalendar/calendar.html', context)


@csrf_protect
def changeFormat(request):
    if request.method == "GET":
        oldFormat = request.session['format']
        calendarFormat = request.GET['format']
        request.session['format'] = calendarFormat

        if (calendarFormat == "monthly"):
            if (oldFormat == "weekly"):
                today = date.today()
                current = today + relativedelta(days=request.session['whichweek']*7)
                request.session['whichmonth'] = ((current.year - date.today().year)*12
                                                 + current.month - today.month)
            monthDays, monthWeeks, header = getWeeks(request.session['whichmonth'])
            d = {'header': header, 'weeks': monthWeeks}
        else:
            if (oldFormat == "monthly"):
                today = date.today()
                current = today + relativedelta(months=request.session['whichmonth'])
                request.session['whichweek'] = (current - today).days/7
            days, hours, dates, header = getDays(request.session['whichweek'])

            d = {'header': header, 'days': days, 'dates': dates}
        return HttpResponse(simplejson.dumps(d))
    else:
        return HttpResponseNotFound()


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
def changeMonth(request):
    if request.method == "POST":
        change = int(request.POST['amount'])
        if (change == 0):
            request.session['whichmonth'] = 0
        else:

            request.session['whichmonth'] += change

        monthDays, monthWeeks, header = getWeeks(request.session['whichmonth'])
        d = {'header': header, 'weeks': monthWeeks}
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
        if(len(request.POST['title']) == 0):
            e = Event(
            description=request.POST['description'],
            location=request.POST['location'],
            start=startDate,
            end=endDate,
        ) 
        else:    
            e = Event(
                title=request.POST['title'],
                description=request.POST['description'],
                location=request.POST['location'],
                start=startDate,
                end=endDate,
            )

        e.save()
        usr = UserProfile.objects.get(user=request.session['fbid'])
        usr.events.add(e)
        if(request.POST.has_key('friendIDs')):
            friendIDs = json.loads(request.POST['friendIDs'])
            storeNotificationForFriends(friendIDs, e)
        #d = {'header': header, 'days': days, 'dates': dates}
        return HttpResponse()
    else:
        return HttpResponseNotFound()

def getNotifications(user):
    events = user.notifications.all();
    return getArrayofWeeklyEvents(events);

def storeNotificationForFriends(friendIDs, e):
    for friendID in friendIDs:
        usr = UserProfile.objects.filter(user=friendID)
        if (len(usr) != 0):
            usr[0].notifications.add(e)

def removeNotification(user, e) :
    user.notifications.remove(e);

@csrf_protect
def getNotificationsRequest(request):
    if request.method == "GET":
        usr = UserProfile.objects.get(user=request.session['fbid'])
        notifs = getNotifications(usr);
        return HttpResponse(simplejson.dumps(notifs));
    else :
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
    
    if (not request.session.__contains__('fbid')):
        d = []
        return HttpResponse(simplejson.dumps(d))

    usr = UserProfile.objects.get(user=request.session['fbid'])
    events = usr.events.filter(start__gte=first).filter(end__lt=last)

    events = events.extra(order_by=['start'])

    d = getArrayofWeeklyEvents(events)
    return HttpResponse(simplejson.dumps(d))

def getArrayofWeeklyEvents(events):
    d = []
    x = 0
    last = 0
    if(len(events) == 0):
        return d

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
        endhour = e.end.hour
        if (e.end.hour == 0):
            endhour = 24
        d.append({
            'title': e.title,
            'start': e.start.hour+e.start.minute/60.0,
            'end': endhour+e.end.minute/60.0,
            'day': ((e.start.weekday()+1) % 7),
            'id': e.id,
            'x': xs[i]/float(widths[i]),
            'width': 1.0/float(widths[i]),
        })
    return d;

@csrf_protect
def populateMonthEvents(request):

    print request.session['whichmonth']

    today = datetime.today() + relativedelta(months=request.session['whichmonth'])
    today = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    delta = timedelta((today.weekday()+1) % 7)
    first = today - delta
    last = today + relativedelta(months=1)
    delta = timedelta((today.weekday()+1) % 7)
    last = last + (timedelta(7) - delta)

    first = first.replace(tzinfo=tz.gettz('UTC'))
    last = last.replace(tzinfo=tz.gettz('UTC'))
    
    if (not request.session.__contains__('fbid')):
            d = []
            return HttpResponse(simplejson.dumps(d))    

    usr = UserProfile.objects.get(user=request.session['fbid'])
    events = usr.events.filter(start__gte=first).filter(end__lt=last)
    events = events.extra(order_by=['start'])
    d = []
    if (len(events) == 0):
        return HttpResponse(simplejson.dumps(d))

    for i in range(len(events)):
        e = events[i]
        d.append({
            'title': e.title,
            'start': e.start.hour+e.start.minute/60.0,
            'end': e.end.hour+e.end.minute/60.0,
            'day': ((e.start - first).days),
            'id': e.id,
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
                'startms': calendar.timegm(event.start.timetuple())*1000,
                'endms': calendar.timegm(event.end.timetuple())*1000,
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
def heatMap(request):
    if request.method == "POST":

        friendIDs = eval(request.POST['data[param]'])
        today = datetime.today() + timedelta(request.session['whichweek']*7)
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)
        delta = timedelta((today.weekday()+1) % 7)
        first = today - delta
        last = first + timedelta(7)

        first = first.replace(tzinfo=tz.gettz('UTC'))
        last = last.replace(tzinfo=tz.gettz('UTC'))
        ratio = [[0 for x in xrange(48)] for x in xrange(7)]         

        total = 0.0;

        for friend in friendIDs :
            timeSlotConsider = [[0 for x in xrange(48)] for x in xrange(7)] 

            usr = UserProfile.objects.filter(user=friend)     
            if(len(usr) == 0):
                continue
            total = total+1.0;
            events = usr[0].events.filter(start__gte=first).filter(end__lt=last)
            events = events.extra(order_by=['start'])
            
            for event in events:
                start = event.start;
                end = event.end;
                day = (start.weekday()+1) % 7
                for i in range(start.hour*2+start.minute/30, end.hour*2+end.minute/30):
                    print i, day
                    if not timeSlotConsider[day][i]:
                        ratio[day][i] += 1;
                    timeSlotConsider[day][i] = True

        days, hours, dates, weekHeader = getDays(request.session['whichweek'])
        d = []
            
        for j in range(len(hours)*2):
            for i in range(len(days)):
                print i, j, ratio[i][j]
                d.append({
                    'ratios': (1-ratio[i][j]/total),
                })

        return HttpResponse(simplejson.dumps(d))
    else:
        return HttpResponseNotFound()


@csrf_protect
def gcal(request):
    events = json.loads(request.POST['responseJSON'])
    usr = UserProfile.objects.get(user=request.session['fbid'])
    if events['items']:
        for event in events['items']:
            if event.has_key('iCalUID'):
                existentEvent = usr.events.filter(gid=event['iCalUID'])
                if(len(existentEvent) != 0):
                    continue
            if not event.has_key('summary'):
                event['summary'] = 'No-Title'
            if not event.has_key('description'):
                event['description'] = ''
            if not event.has_key('location'):
                event['location'] = ''
            if not event.has_key('start'):
                continue
            if not event.has_key('end'):
                continue
            if not event.has_key('iCalUID'):
                event['iCalUID'] = ''
            if event['end'].has_key('date') and len(event['end']['date']) <=10 :
                continue
            startTime = datetime.strptime(event['start']['dateTime'][:-6], googleDateString)
            startTime = startTime.replace(tzinfo=tz.gettz('UTC'))
            endTime = datetime.strptime(event['end']['dateTime'][:-6], googleDateString)
            endTime = endTime.replace(tzinfo=tz.gettz('UTC'))
            e = Event(title=event['summary'],
                      description=event['description'],
                      location=event['location'],
                      start=startTime,
                      end=endTime,
                      gid=event['iCalUID']
                      )
            e.save()
            usr.events.add(e)
    return HttpResponse()

@csrf_protect
def acceptNotification(request):    
    if(request.method == POST):
        usr = UserProfile.objects.filter(user=request.session['fbid'])
        event = Event.objects.get(id=request.POST['id'])
        removeNotification(usr, event)
        usr.events.add(e)
    else:
        HttpResponseNotFound();

@csrf_protect
def rejectNotification(request):
    if(request.method == POST):
        usr = UserProfile.objects.filter(user=request.session['fbid'])
        event = Event.objects.get(id=request.POST['id'])
        removeNotification(usr, event)
    else:
        HttpResponseNotFound();    

@csrf_protect
def makeUser(request):
    if request.method == "GET":
        name = request.GET['name']
        fbid = request.GET['fbid']
        
        d = [];

        if (request.session.__contains__('fbid') and not (request.session['fbid'] == fbid)):
            d.append({'changed': True, })
        request.session['fbid'] = fbid
        usr = UserProfile.objects.filter(user=fbid)

        if(len(usr) != 0):
            print  usr[0].name
            return HttpResponse(simplejson.dumps(d))
        
        prof = UserProfile(user=fbid,name=name) 
        prof.save()

        return HttpResponse()
    else :
        return HttpResponseNotFound()        

@csrf_protect
def deleteCookie(request):
    if not request.session.get('fbid')==None:
        del request.session['fbid']
    return HttpResponse()
