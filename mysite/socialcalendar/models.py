from django.db import models
from django.contrib.auth.models import User

class ExceptionDate(models.Model):
    exceptionTime = models.DateTimeField()

    def __unicode__(self):
        return self.exceptionTime


class Event(models.Model):

    TYPE_CHOICES = (
        ('AVPU', 'Available-Public'),
        ('AVPR', 'Available-Private'),
        ('BUPU', 'Busy-Public'),
        ('BUPR', 'Busy-Private')
    )
    kind = models.CharField(max_length=4,
                            choices=TYPE_CHOICES,
                            default='BUPU')
    title = models.TextField(default = 'No-Title')
    location = models.TextField(default = '')
    description = models.TextField(default='No-Description')
    start = models.DateTimeField('Event start')
    end = models.DateTimeField('Event end')
    gid = models.TextField(default = "")
    repeat = models.BooleanField(default = False)
    recurrence = models.TextField(default= "")
    exceptions = models.ManyToManyField(ExceptionDate, related_name = 'ExceptionDate')
    repeatID = models.TextField(default = "")
    unseen = models.ManyToManyField("Unseen", related_name = 'Unseen')

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ('title',)

class UserProfile(models.Model):
    #home_address = models.TextField()
    #user = models.CharField(max_length=100, unique=True)
    user = models.CharField(max_length=100, blank=True)
    actualUser=models.ForeignKey(User)
    events = models.ManyToManyField(Event, related_name = 'events')
    name = models.CharField(max_length=30)
    notifications = models.ManyToManyField(Event, related_name = 'notification')
    creators = models.ManyToManyField(Event, related_name = 'creators')
    accepted = models.ManyToManyField(Event, related_name='accepted')
    rejected = models.ManyToManyField(Event, related_name ='rejected')
    unanswered = models.ManyToManyField(Event, related_name='unanswered')
 

    def __unicode__(self):
        return self.name

class Name(models.Model):
    name = models.CharField(max_length=30)
    linkedEvent = models.ForeignKey(Event,related_name = 'linkedEvent')

    def __unicode__(self):
        return self.name

class Comment(models.Model):
    comment = models.TextField(default='')
    commenter = models.ForeignKey(UserProfile, related_name = 'commenter', blank=True, null = True)
    name = models.TextField(default = '')
    date = models.DateTimeField('Comment Time')
    event = models.ForeignKey(Event, related_name = 'event')
    commentID = models.TextField(default = '')
    def __unicode__(self):
        return self.comment

class Unseen(models.Model):
    people = models.ForeignKey("UserProfile", related_name = 'unseen')
    commentID = models.TextField(default = '')
    def __unicode__(self):
        return self.commentID 

