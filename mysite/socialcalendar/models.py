from django.db import models
from django.contrib.auth.models import User

class ExceptionDate(models.Model):
    exceptionTime = models.DateTimeField()
    
    def __unicode__(self):
        return self.exceptionTime    

        
class Event(models.Model):
    title = models.CharField(max_length=30, default = 'No-Title')
    location = models.CharField(max_length=30)
    description = models.TextField()
    start = models.DateTimeField('Event start')
    end = models.DateTimeField('Event end')
    gid = models.CharField(max_length=100)
    repeat = models.BooleanField(default = False)
    recurrence = models.CharField(max_length = 100)
    exceptions = models.ManyToManyField(ExceptionDate, related_name = 'ExceptionDate')
    kind = models.CharField(max_length = 30)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ('title',)

class UserProfile(models.Model):
    #home_address = models.TextField()
    user = models.CharField(max_length=100, unique=True) #models.ForeignKey(User, unique=True)
    events = models.ManyToManyField(Event, related_name = 'events')
    name = models.CharField(max_length=30)
    notifications = models.ManyToManyField(Event, related_name = 'notification')
    creators = models.ManyToManyField(Event, related_name = 'creators') 
    accepted = models.ManyToManyField(Event, related_name='accepted')
    rejected = models.ManyToManyField(Event, related_name ='rejected')
    unanswered = models.ManyToManyField(Event, related_name='unanswered')


    def __unicode__(self):
        return self.name