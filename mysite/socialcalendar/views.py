import cgi
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
import calendar
from datetime import date, timedelta, datetime
from dateutil.rrule import *
from dateutil.parser import *

from dateutil import tz
from django.utils import simplejson
from dateutil.relativedelta import relativedelta
from socialcalendar.models import Event
from socialcalendar.models import UserProfile
from socialcalendar.models import ExceptionDate
from socialcalendar.models import Name
from socialcalendar.models import Comment
from socialcalendar.models import Unseen



from itertools import chain

import json

import random

import re
import math
idfeDateString = "%m%d%Y%I%M%p"
untilString = "%Y%m%dT000000Z"
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
    if request.GET.has_key('id'):
        event = Event.objects.filter(id=findIdOfEvent(request.GET['id']))
        if len(event) != 0 and (event[0].kind == 'AVPU' or event[0].kind == 'AVPR' or event[0].kind == 'BUPU' or event[0].kind == 'BUPR'):
            e = event[0]
            if(request.session.has_key('fbid')):
                unseen = Unseen.objects.filter(people = UserProfile.objects.get(user=request.session['fbid'])).filter(commentID=request.GET['id'])
                for u in unseen:
                    e.unseen.remove(u)
            creators = list(e.creators.all().values())
            if e.description == '':
                e.description = "No-Description"
            i = 0
            if request.session.has_key('fbid'):
                i = 1
            eid = request.GET['id']
            location = e.location;
            if location == "":
                location = "No-Location"
            context = {
                'title': e.title,
                'description':e.description,
                'location':location,
                'start': e.start.strftime(dateString),
                'end': e.end.strftime(dateString),
                'creators' : creators,
                'coming' : list(e.events.all().values())+list(e.linkedEvent.all().values()),
                'comments': getListOfCommentsNotReverse(e, request.GET['id']),
                'rejected' : list(e.rejected.all().values()),
                'id':eid,
                'loggedIn': i,
                }
            return render(request, 'socialcalendar/event.html', context)

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

    usr = UserProfile.objects.get(user=request.session['fbid'])
    context = {
        'format': request.session['format'],
        'days': days,
        'hours': hours,
        'dates': dates,
        'header': header,
        'events': Event.objects.all(),
        'monthDays': monthDays,
        'monthWeeks': monthWeeks,
        'hasNotification': usr.notifications.count() > 0,
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
def goToEvent(request):
    if request.method == "POST":
        event = Event.objects.get(id=findIdOfEvent(request.POST['id']))

        today = datetime.today()
        today = today.replace(tzinfo=tz.gettz('UTC'))
        #monday1 = (today - timedelta(days=today.weekday()+1))
        #monday2 = (event.start - timedelta(days=event.start.weekday()+1))
        #delta_day = target_day - datetime.now().isoweekday()
        sunday1 = today - timedelta(days=(today.isoweekday() %7))
        sunday1 = sunday1.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
        sunday2 = event.start - timedelta(days=(event.start.isoweekday() %7), hours = event.start.hour, minutes = event.start.minute)
        sunday2 = sunday2.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
        print sunday1, sunday2
        request.session['whichweek'] = int((sunday2 - sunday1).days/7.0)

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
        if(not request.POST.has_key('startTime') or request.POST['startTime'] == "" or not request.POST.has_key('endTime') or request.POST['endTime'] == "") :
            return HttpResponse()

        startDate = datetime.strptime(request.POST['startTime'],
                                      dateString)
        endDate = datetime.strptime(request.POST['endTime'],
                                    dateString)
        startDate = startDate.replace(tzinfo=tz.gettz('UTC'))
        endDate = endDate.replace(tzinfo=tz.gettz('UTC'))
        startDate = startDate.astimezone(tz.gettz('UTC'))
        endDate = endDate.astimezone(tz.gettz('UTC'))

        rrule = ""
        repeat = False
        if request.POST.has_key('RRULE'):
            rrule = getrrule(request.POST['RRULE'])
            repeat = True

        title = "No-Title"

        if(len(request.POST['title']) != 0):
            title = request.POST['title']

        usr = UserProfile.objects.get(user=request.session['fbid'])
        e = createEvent(start=startDate, end=endDate, recurrence = rrule, usr = usr, title=title, description=request.POST['description'], location=request.POST['location'], kind = request.POST['kind'], repeat = repeat)

        if(request.POST.has_key('friendIDs')):
            friendIDs = json.loads(request.POST['friendIDs'])
            storeNotificationForFriends(friendIDs, e)
            #d = {'header': header, 'days': days, 'dates': dates}
        return HttpResponse()
    else:
        return HttpResponseNotFound()

def createEvent(start, end, recurrence, usr = None, title = "No-Title", description = "", location = "", kind = "BUPR", repeat = False):
    if usr == None:
        return
    if end <= start:
        end = start + timedelta(minutes = 30)
    e = Event(
        title=title,
        description=description,
        location=location,
        start=start,
        end=end,
        kind = kind,
        recurrence = recurrence,
        repeat = repeat,
        )
    e.save()
    usr.creators.add(e)
    usr.events.add(e)

    return e

def getrrule(rrule):
    rule = str(rrule);
    until = re.findall(r"../../.............", str(rrule));
    if len(until) > 0:
        date = datetime.strptime(until[0], dateString)
        rule = str(rule).replace(until[0], date.strftime(untilString))
    return rule

def getNotifications(user):
    events = user.notifications.all();
    d = []
    for event in events:
        d.append({
            'id':event.id,
            'creators':getCreators(event),
            'title':event.title
        });
    return d


def storeNotificationForFriends(friendIDs, e):
    usr = UserProfile.objects.filter(user__in=friendIDs).exclude(notifications = e).exclude(events = e)
    for user in usr:
        user.unanswered.add(e)
        user.notifications.add(e)

    return len(usr) > 0

def removeNotification(user, e) :
    user.notifications.remove(e);


@csrf_protect
def addFriendsToEvent(request):
    if request.method == "POST":
        event = Event.objects.get(id=findIdOfEvent(request.POST['id']))
        friendIDs = json.loads(request.POST['friendIDs'])
        notif = storeNotificationForFriends(friendIDs, event)
        d = []
        d.append({"notif": notif})
        return HttpResponse(simplejson.dumps(d));
    else :
        return HttpResponseNotFound()

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

    events = getAllEvents(usr, first, last, ['AVPU', 'AVPR', 'BUPU', 'BUPR'])

    d = getArrayofWeeklyEvents(events, usr)
    return HttpResponse(simplejson.dumps(d))

def getArrayofWeeklyEvents(events, usr, notif = False): # events given to method sorted based on start time
    d = [] # data?
    x = 0 # x position of event on calendar
    first = True # boolean - whether this is the first event of a day
    groupStart = 0
    # groupEnd = 0
    # last = 0 

    #    print "events: ", events

    #   '''
    #  print "length:", len(events)
    # print "events:", events
    #print "usr:", usr
    # print events[0]
    # '''

    if(len(events) == 0): # if the usr doesn't have any events in the given week
        return d # return an empty array

    latestStartTime = events[0].start # initialized to start time of very first event
    # latest start time in the current group

    # biggestEnd = events[0].end # initialized to end time of very first event

    widths = [] # array of event widths
    xs = [] # x positions of events

    #   '''
    #  currDate = events[0].start.date() # initialized to date of first event
    # print "test: ", (events[1].start.hour + events[1].start.minute/60.0)
    #print "date: ", currDate
    #'''

    # HERE!

    # get the date of the first event
    currDate = events[0].start.date() # initialized to date of first event

    # keep track of i; initialize i to 0
    i = 0

    # while i < len(events) (if this is true, then events[i] is a valid event)
    while i < len(events):

    #     if the start date of event[i] is equal to the current date 
    #     # can't use this as an indicator for first event of the day
    #     # because we want the first event of the day to have its date stored in the present date at the beginning
    #     # unless we set present date to null at the beginning (possible idea -- try that later)            
    #         if it's the first event of the day
    #             simply append x as is (xs.append(x))
    #             set groupStart = i
    #             set first = false

        # event is on the same date as the previous event
        if events[i].start.date() == currDate:
            # only way it could be first in this case is if it's the very first event
            if first:
            #           print "THIS OCCURS NOW!"
                groupStart = i
                first = False

            # not first event of the day
            else:
                # if start time is less than 30 minutes after most recent start time
                # then put adjacent to other event
                # increment x
                # and append x to xs
                # keep same precedence
                prevTime = (latestStartTime.hour + latestStartTime.minute/60.0)
                if (events[i].start.hour + events[i].start.minute/60.0 - prevTime) < 0.5:
                    x += 1
                    #xs.append(x)

                    # else (start time is at least 30 min after most recent start time)
                    #                 assign widths to all items in previous group (groupStart, i) -- not including i
                    #                 start a new group (set groupStart = i and set x = 0)
                    #                 give new group higher precedence in terms of overlay
                else:
                    for j in range(groupStart, i):
                    #                        print "j:", j
                        widths.append(x+1)
                    groupStart = i
                    x = 0
                    # GIVE NEW GROUP HIGHER PRECEDENCE 

        # event is on a date different from the previous event
        else:
            for j in range(groupStart, i):
            #               print "j:", j
                widths.append(x+1)
            currDate = events[i].start.date() # reset the current date
            # reset variables
            # first = True
            x = 0
            groupStart = i

        # update most recent start time (no matter what, right?)
        latestStartTime = events[i].start

        # increment i
        i += 1

        # append x
        xs.append(x)

    # # this is probably very necessary
    # after loop finishes, set widths for (groupStart, i) (not including i)
    for j in range(groupStart, i):
    #  print "j:", j
        widths.append(x+1)

    '''
    for i in range(len(events)-1): # iterate over every event
            if (events[i].start.date() != currDate):
            currDate = events[i].start.date()
            xs.append(x) 
 
        prevTime = (latestStartTime.hour + latestStartTime.minute/60.0)
        print "prevTime:", prevTime
        print "currTime:", (events[i].start.hour + events[i].start.minute/60.0)
        if (events[i].start.hour + events[i].start.minute/60.0 - prevTime) < 0.5: # add to group
            print "i:", i
            x = x + 1

        else:
            for j in range(last, i+1):
                widths.append(x+1)
            # biggestEnd = events[i+1].end
            x = 0
            last = i+1

            # print 'biggestEnd: ', biggestEnd
            print 'last: ', last

            # last keeps track of which event was last in the array

        latestStartTime = events[i].start # update latest start time
   
    for i in range(len(events)-1): # iterate over every event
        xs.append(x) 
        if events[i].end > biggestEnd: # update latest end time
            biggestEnd = events[i].end
        if biggestEnd > events[i+1].start:
            x = x + 1
        else:
            for j in range(last, i+1):
                widths.append(x+1)
            biggestEnd = events[i+1].end
            x = 0
            last = i+1

            print 'biggestEnd: ', biggestEnd
            print 'last: ', last

            # last keeps track of which event was last in the array


    xs.append(x)
    for j in range(last, len(events)):
        widths.append(x+1)
    '''

    # TAKE THIS OUT LATER
    # print len(xs)
    # print len(widths)

    for i in range(len(events)):
    #        print "xs length:", len(xs)
    #       print "widths length:", len(widths)

    #        print "xs:", xs
    #       print "widths:", widths

        e = events[i]
        endhour = e.end.hour
        if (e.end.day > e.start.day):
            endhour = 24
        eID = e.id;
        creator0 = None

        if e.repeat:
            eID = e.repeatID;
            creator0 = list(e.creators.values())
        elif (len(e.creators.all()) > 0):
            creator0 = list(e.creators.all().values())

        d.append({
            'title': cgi.escape(e.title),
            'start': e.start.hour+e.start.minute/60.0,
            'end': endhour+e.end.minute/60.0 + .1,
            'day': ((e.start.weekday()+1) % 7),
            'id': eID,
            'x': xs[i]/float(widths[i]),
            'width': 1.0/float(widths[i]),
            'creators': creator0,
            'canEdit': canEdit(usr, e),
            'repeat': e.repeat,
            'kind': e.kind,
            'notif': usr.notifications.filter(id=e.id).count() >= 1,
            'newComment':e.unseen.filter(people = usr).filter(commentID = eID).count() >= 1,
            })
        #      print 'x:',  xs[i]
        #     print 'width:', 1.0/float(widths[i])

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
    events = getAllEvents(usr, first, last, ['AVPU', 'AVPR', 'BUPU', 'BUPR'])
    d = []
    if (len(events) == 0):
        return HttpResponse(simplejson.dumps(d))

    for i in range(len(events)):
        e = events[i]

        eID = e.id
        creator0 = None

        if e.repeat:
            eID = e.repeatID
            creator0 = list(e.creators.values())
        elif (len(e.creators.all()) > 0):
            creator0 = list(e.creators.all().values())

        d.append({
            'title': cgi.escape(e.title),
            'start': e.start.hour+e.start.minute/60.0,
            'end': e.end.hour+e.end.minute/60.0,
            'day': ((e.start - first).days),
            'id': eID,
            'creators': creator0,
            'canEdit': canEdit(usr, e),
            'repeat': e.repeat,
            'kind': e.kind,
            'notif': usr.notifications.filter(id=e.id).count() >= 1,
            'newComment':e.unseen.filter(people = usr).filter(commentID = eID).count() >= 1,
            })

    return HttpResponse(simplejson.dumps(d))


@csrf_protect
def getEventData(request):

    if request.method == "POST":
        eid = request.POST['id']
        events = Event.objects.filter(id=findIdOfEvent(eid))
        usr = UserProfile.objects.get(user=request.session['fbid'])

        if (len(events) != 1):
            return HttpResponseNotFound()
        else:
            event = list(events)[0]
            start = event.start
            end = event.end

            if event.repeat:
                start = datetime.strptime(eid[eid.rfind("_")+1:], idfeDateString)
                end = start + (event.end - event.start)
            d = {
                'title': event.title,
                'description': event.description,
                'location': event.location,
                'start': start.strftime(dateString),
                'end': end.strftime(dateString),
                'startms': calendar.timegm(event.start.timetuple())*1000,
                'endms': calendar.timegm(event.end.timetuple())*1000,
                'id': event.id,
                'canEdit': canEdit(UserProfile.objects.get(user=request.session['fbid']), event),
                'kind': event.kind,
                'notif': usr.notifications.filter(id=event.id).count() >= 1,
                'coming':list(event.events.all().values()),
                'repeat':event.repeat,
                }
            return HttpResponse(simplejson.dumps(d))
    else:
        return HttpResponseNotFound()


@csrf_protect
def deleteEvent(request):

    if request.method == "POST":
        usr = UserProfile.objects.get(user=request.session['fbid'])
        eid = request.POST['id']
        event = Event.objects.get(id=findIdOfEvent(request.POST['id']))

        if event.events.filter(user = usr.user).count() > 0:
            event.rejected.add(usr)

        if canEdit(usr, event):
            if not event.repeat or request.POST['all'] == 'all':
                event.delete()
            else:
                deleteSingleRecurrence(event, (datetime.strptime(eid[eid.rfind("_")+1:], idfeDateString)).replace(tzinfo=tz.gettz('UTC')))
        else:
            usr.events.remove(event)
        return HttpResponse()
    else:
        return HttpResponseNotFound()


def deleteSingleRecurrence(e, time):
    if(e.repeat):
        ex = ExceptionDate(exceptionTime=time)
        ex.save()
        e.exceptions.add(ex)
    return

@csrf_protect
def editEvent(request):
    if request.method == "POST":
        if(not request.POST.has_key('startTime')) :
            return HttpResponse()

        event = Event.objects.get(id=findIdOfEvent(request.POST['id']))

        startDate = datetime.strptime(request.POST['startTime'],
                                      dateString)
        endDate = datetime.strptime(request.POST['endTime'],
                                    dateString)
        startDate = startDate.replace(tzinfo=tz.gettz('UTC'))
        endDate = endDate.replace(tzinfo=tz.gettz('UTC'))
        startDate = startDate.astimezone(tz.gettz('UTC'))
        endDate = endDate.astimezone(tz.gettz('UTC'))
        if(startDate > endDate):
            return HttpResponse()
        rrule = ""
        repeat = False
        if request.POST.has_key('RRULE'):
            rrule = getrrule(request.POST['RRULE'])
            repeat = True

        title = "No-Title"

        if(len(request.POST['title']) != 0):
            title = request.POST['title']

        if(event.repeat and request.POST.has_key('all') and request.POST['all'] == 'this'):
            usr = UserProfile.objects.get(user=request.session['fbid'])
            createException(request.POST['id'], event)
            createEvent(title=title, description=request.POST['description'], location=request.POST['location'], start=startDate, end=endDate, kind = request.POST['kind'], recurrence = rrule, repeat = repeat, usr = usr)
            return HttpResponse()
        event.title=title
        event.description=request.POST['description']
        event.location=request.POST['location']
        event.start=startDate
        event.end=endDate
        event.kind = request.POST['kind']
        event.recurrence = rrule
        event.repeat = repeat
        event.save()

        return HttpResponse()
    else:
        return HttpResponseNotFound()


@csrf_protect
def changeStart(request):
    if request.method == "POST":
        eid = request.POST['id']
        event = Event.objects.get(id=findIdOfEvent(eid))
        if(event.repeat):
            startDate = datetime.strptime(request.POST['startTime'], dateString)

            startDate = startDate.replace(tzinfo=tz.gettz('UTC'))
            startDate = startDate.astimezone(tz.tzlocal())

            eventLength = event.end - event.start
            start = startDate
            end = startDate + eventLength

            createException(eid, event)

            e = Event(
                title=event.title,
                description=event.description,
                location=event.location,
                start=start,
                end=end,
                kind = event.kind,
                )

            e.save()
            e.notification.add(*list(event.notification.all()))
            e.events.add(*list(event.events.all()))
            e.creators.add(*list(event.creators.all()))
            comments = Comment.objects.filter(commentID=eid)
            e.event.add(*list(comments))
            unseen = Unseen.objects.filter(commentID=eid)

            for u in unseen:
                u.commentID = e.id
                u.save()

            e.unseen.add(*list(unseen))
            comments.update(commentID=e.id)
            return HttpResponse()

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
        busy = [[[] for j in range(48)] for i in range(7)]
        total = 0.0


        usrs = UserProfile.objects.filter(user__in=friendIDs)
        for usr in usrs:
            timeSlotConsider = [[0 for x in xrange(48)] for x in xrange(7)]

            total = total+1.0
            events = getAllEvents(usr, first, last, ['BUPU'])

            for event in events:
                start = event.start
                end = event.end
                day = (start.weekday()+1) % 7
                for i in range(int(start.hour*2+math.floor(start.minute/30.0)), int(end.hour*2+math.ceil(end.minute/30.0))):
                    if not timeSlotConsider[day][i]:
                        ratio[day][i] += 1
                        busy[day][i].append(usr.name)
                    timeSlotConsider[day][i] = True

        days, hours, dates, weekHeader = getDays(request.session['whichweek'])
        d = []
        if not total == 0:
            for j in range(len(hours)*2):
                for i in range(len(days)):
                    d.append({
                        'ratios': (1-ratio[i][j]/total),
                        'busy': busy[i][j],
                        })

        return HttpResponse(simplejson.dumps(d))
    else:
        return HttpResponseNotFound()


@csrf_protect
def gcal(request):

    events = json.loads(request.POST['responseJSON'])
    usr = UserProfile.objects.get(user=request.session['fbid'])
    if events.has_key('items') and events['items']:
        for event in events['items']:
            recurring = False;
            recurrence = '';


            if event.has_key('originalStartTime') and event.has_key('recurringEventId') :
                ev = usr.events.filter(gid=event['recurringEventId'])

                if len(ev) > 0 and ev[0].exceptions.filter(exceptionTime=(datetime.strptime(event['originalStartTime']['dateTime'][:-6], googleDateString)).replace(tzinfo=tz.gettz('UTC'))).count() == 0:
                    ex = ExceptionDate(exceptionTime=(datetime.strptime(event['originalStartTime']['dateTime'][:-6], googleDateString)).replace(tzinfo=tz.gettz('UTC')))
                    ex.save()
                    ev[0].exceptions.add(ex)
                    if not event.has_key('start'):
                        continue

            if event.has_key('id'):
                existentEvent = usr.events.filter(gid=event['id'])
                if(len(existentEvent) != 0):
                    continue
            if not event.has_key('summary'):
                event['summary'] = 'No-Title'
            if not event.has_key('description'):
                event['description'] = 'No-Description'
            if not event.has_key('location'):
                event['location'] = ''
            if not event.has_key('start'):
                continue
            if not event.has_key('end'):
                continue
            if not event.has_key('id'):
                event['id'] = 'googleEvent'
            if event['end'].has_key('date') and len(event['end']['date']) <=10 :
                continue

            startTime = datetime.strptime(event['start']['dateTime'][:-6], googleDateString)
            startTime = startTime.replace(tzinfo=tz.gettz('UTC'))
            endTime = datetime.strptime(event['end']['dateTime'][:-6], googleDateString)
            endTime = endTime.replace(tzinfo=tz.gettz('UTC'))


            if event.has_key('recurrence') and len(event['recurrence']) > 0:
                recurring = True;
                if not 'RRULE' in event['recurrence'][0] and len(event['recurrence']) > 1 and 'RRULE' in event['recurrence'][1]:
                    until = re.match(".*UNTIL=........", event['recurrence'][1]);
                    if until is not None:
                        recurrence = event['recurrence'][1].replace(until.group(0), until.group(0)+"T000000Z");
                else:
                    recurrence = event['recurrence'][0].replace("035959", "000000"); #.replace('u\'', '\'').replace("[\'", "").replace('\']', '')

            e = Event(title=event['summary'],
                      description=event['description'],
                      location=event['location'],
                      start=startTime,
                      end=endTime,
                      gid=event['id'],
                      repeat=recurring,
                      recurrence=recurrence,
                      kind = 'BUPU',
                      )
            e.save()
            usr.creators.add(e);
            usr.events.add(e)
    return HttpResponse()

@csrf_protect
def acceptNotification(request):
    if(request.method == 'POST'):
        usr = UserProfile.objects.get(user=request.session['fbid'])
        event = Event.objects.get(id=findIdOfEvent(request.POST['eventID']))
        event.unanswered.remove(usr)
        removeNotification(usr, event)
        usr.events.add(event)
        return HttpResponse();
    else:
        HttpResponseNotFound();

@csrf_protect
def rejectNotification(request):
    if(request.method == 'POST'):
        usr = UserProfile.objects.get(user=request.session['fbid'])
        event = Event.objects.get(id=findIdOfEvent(request.POST['eventID']))
        event.unanswered.remove(usr)
        usr.unanswered.remove(event)
        usr.rejected.add(event)
        removeNotification(usr, event)

        return HttpResponse();
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
            return HttpResponse(simplejson.dumps(d))

        prof = UserProfile(user=fbid, name=name)
        prof.save()

        return HttpResponse()
    else :
        return HttpResponseNotFound()

@csrf_protect
def deleteCookie(request):
    if not request.session.get('fbid')==None:
        del request.session['fbid']
    return HttpResponse()

def getWeeklyRecurringEvents(events, first, last):
    totalForWeek = []
    for event in events:
        try:
            rule = rrulestr(event.recurrence, dtstart = event.start)
            times = rule.between(first, last, inc=True)
        except:
            continue
        for time in times:
            if event.exceptions.filter(exceptionTime=time).count() > 0:
                continue

            e = tempEvent(
                title=event.title,
                description=event.description,
                location=event.location,
                start=datetime(time.year ,time.month ,time.day , event.start.hour, event.start.minute).replace(tzinfo=tz.gettz('UTC')),
                end=datetime(time.year, time.month, time.day, event.end.hour, event.end.minute).replace(tzinfo=tz.gettz('UTC')),
                repeat = True,
                repeatID = str(event.id) + '_' + time.strftime(idfeDateString),
                eid = event.id,
                creators = event.creators.all(),
                kind = event.kind,
                unseen = event.unseen
            )
            e.id = event.id
            totalForWeek.append(e)

    return totalForWeek

# change getAllEvents to add kinds array parameter
def getAllEvents(usr, first, last, kinds):
    events = usr.events.filter(start__gte=first).filter(end__lt=last).filter(repeat=False).filter(kind__in = kinds)
    events = chain(events, getNotificationsForWeek(usr, first, last, kinds))
    events = sorted(chain(events, getWeeklyRecurringEvents(usr.events.filter(repeat=True), first, last)), key=lambda event: event.start)
    return events

def getNotificationsForWeek(user, first, last, kinds):
    events = user.notifications.filter(repeat=False).filter(start__gte=first).filter(end__lt=last)
    weeklyEvents = user.notifications.filter(repeat=True).filter(kind__in = kinds)
    events = chain(events, getWeeklyRecurringEvents(weeklyEvents, first, last))
    return events


def canEdit(usr, event):
    return (usr in event.creators.all())

def addCreators(event, creatorsArray):
    usrs = UserProfile.objects.filter(user__in=creatorsArray)
    for user in usrs:
        event.creators.add(user)

@csrf_protect
def addCreatorsToEvent(request):
    if request.method == "POST":
        event = Event.objects.get(id=findIdOfEvent(request.POST['id']))
        friendIDs = json.loads(request.POST['friendIDs'])
        addCreators(event, friendIDs)
        return HttpResponse();
    else:
        return HttpResponseNotFound()


def findIdOfEvent(idToSearch):
    if idToSearch.rfind("_") == -1:
        return idToSearch
    return idToSearch[0: idToSearch.rfind("_")]

class tempEvent:
    def __init__(self, title, description, location, start,end, repeat, repeatID, eid, creators, kind, unseen):
        self.title = title
        self.description = description
        self.location = location,
        self.start = start
        self.end = end
        self.repeat = repeat
        self.repeatID = repeatID
        self.id = eid
        self.creators = creators
        self.kind = kind
        self.unseen = unseen


@csrf_protect
def addName(request):
    if request.method == "GET":
        if request.GET['name'] == '':
            return HttpResponse()
        e = Event.objects.get(id = findIdOfEvent(request.GET['id']))
        n = Name(name = request.GET['name'], linkedEvent=e)
        n.save()
        d = []
        d.append({"person": cgi.escape(request.GET['name'])});
        return HttpResponse(simplejson.dumps(d))
    else:
        return HttpResponseNotFound()


@csrf_exempt
def comment(request):
    if request.method == "POST":
        event = Event.objects.get(id=findIdOfEvent(request.POST['id']))
        usr = None

        name = "No-Name"

        if request.POST.has_key('name'):
            name = request.POST['name']

        if request.session.has_key('fbid'):
            usr = UserProfile.objects.get(user=request.session['fbid'])
            name = usr.name
        if name == None:
            return HttpResponse()

        addComment(commenter=usr, event=event, comment=request.POST['comment'], name = name, date = datetime.today().replace(tzinfo=tz.gettz('UTC')), commentID = request.POST['id'])
        d = []
        if usr != None:
            users = event.events.exclude(user = usr.user).exclude(unseen__in = list(event.unseen.all()))
        else:
            users = event.events.exclude(unseen__in = list(event.unseen.all()))
        for user in users:
            u = Unseen(
                people = user,
                commentID = request.POST['id'],
                )
            u.save()
            event.unseen.add(u)
        d.append({
            'commenter': name,
            'comment':cgi.escape(request.POST['comment']),
            'date':  datetime.today().replace(tzinfo=tz.gettz('UTC')).strftime(dateString)
        })

        return HttpResponse(simplejson.dumps(d))
    else:
        return HttpResponseNotFound()

def addComment(commenter, name, date, event, comment, commentID):
    if commenter == None:
        c = Comment(event=event, comment = comment, name = name, date = date, commentID=commentID);
    else :
        c = Comment(commenter = commenter, event=event, comment = comment, name = name, date = date, commentID=commentID);
    c.save()

def getListOfComments(e, commentID = ''):
    comments = e.event.filter(commentID=commentID).values('name', 'date','comment').order_by('date').reverse()
    d = []
    for comment in comments:
        d.append({
            'name': cgi.escape(comment['name']),
            'date': comment['date'].strftime(dateString),
            'comment': cgi.escape(comment['comment']),
            })
    return d

def getListOfCommentsNotReverse(e, commentID =''):
    comments = e.event.filter(commentID=commentID).values('name', 'date','comment').order_by('date').reverse()
    d = []
    for comment in comments:
        d.append({
            'name': comment['name'],
            'date': comment['date'].strftime(dateString),
            'comment': comment['comment'],
            })
    return d

@csrf_protect
def getComments(request):
    if request.method == "GET":
        eid = request.GET['id'];
        event = Event.objects.get(id=findIdOfEvent(eid));

        if(request.session.has_key('fbid')):
            u = Unseen.objects.filter(people = UserProfile.objects.get(user=request.session['fbid'])).filter(commentID = eid)
            for u0 in u:
                event.unseen.remove(u0)

        return HttpResponse(simplejson.dumps(getListOfComments(event, eid)))
    else:
        return HttpResponseNotFound()

@csrf_protect
def getPeople(request):
    if request.method == "GET":
        event = Event.objects.get(id=findIdOfEvent(request.GET['id']));
        d = {'creators': getCreators(event),
             'coming': getComing(event),
             'rejected': getRejected(event),
             'unanswered': getUnanswered(event)}
        return HttpResponse(simplejson.dumps(d))
    else:
        return HttpResponseNotFound()

def getCreators(e):
    return list(e.creators.values())

def getComing(e):
    return list(e.events.all().values())+list(e.linkedEvent.all().values())

def getRejected(e):
    return list(e.rejected.all().values())

def getUnanswered(e):
    return list(e.unanswered.all().values())

def createException(eid, event):
    ex = ExceptionDate(exceptionTime=(datetime.strptime(eid[eid.rfind("_")+1:], idfeDateString)).replace(tzinfo=tz.gettz('UTC')))
    ex.save()
    event.exceptions.add(ex)


@csrf_protect
def getUsersWithAccount(request):
    if request.method == "POST":
        validUsers = list(UserProfile.objects.filter(user__in=json.loads(request.POST['id[param]'])).values('user'))
        return HttpResponse(simplejson.dumps(validUsers))
    else:
        return HttpResponseNotFound()

