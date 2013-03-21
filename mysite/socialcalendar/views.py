from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
import calendar
from datetime import date, timedelta
from django.utils import simplejson


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


def index(request):

    #if (not request.session.__contains__('whichweek')):
    #    request.session['whichweek'] = 0

    days, hours, dates, header = getDays()
    context = {
        'days': days,
        'hours': hours,
        'dates': dates,
        'header': header,
    }

    return render(request, 'socialcalendar/calendar.html', context)


def ajax(request):
    #request.session['whichweek'] += 1
    if request.method == "POST":
        days, hours, dates, header = getDays(int(request.POST['amount']))# request.session['whichweek'])
        d = {'header': header, 'days': days, 'dates': dates}
        return HttpResponse(simplejson.dumps(d))
    else:
        return HttpResponseNotFound()
