from django.db import models
from django.contrib.auth.models import User


class Event(models.Model):
    title = models.CharField(max_length=30, default = 'No-Title')
    location = models.CharField(max_length=30)
    description = models.TextField()
    start = models.DateTimeField('Event start')
    end = models.DateTimeField('Event end')
    gid = models.CharField(max_length=100)
    repeat = models.BooleanField(default = False)
    recurrence = models.CharField(max_length = 100)

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

    def __unicode__(self):
        return self.user
