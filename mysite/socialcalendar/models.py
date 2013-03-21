from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    title = models.CharField(max_length=30)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ('title',)

class UserProfile(models.Model):
    home_address = models.TextField()
    user = models.ForeignKey(User, unique=True)
    events = models.ManyToManyField(Event)
    
    def __unicode__(self):
        return self.user.name
