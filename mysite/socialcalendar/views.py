from django.http import HttpResponse
from django.shortcuts import render
import calendar

def index(request):
        days = calendar.day_name
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
        context = {
                'days': days,
                'hours': hours,
                }
        print days[0]
            
        return render(request, 'socialcalendar/calendar.html', context)
