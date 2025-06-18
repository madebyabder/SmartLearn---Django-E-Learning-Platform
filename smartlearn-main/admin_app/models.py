from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django import forms


class ActivityLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} ({self.timestamp})"


class Event(models.Model):
    title = models.CharField(max_length=100)
    date = models.DateTimeField()
    enseignants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='events', blank=True)


class VideoConference(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    is_cancelled = models.BooleanField(default=False)
    


