from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Recordings(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    url = models.CharField(max_length=1000)
    name = models.CharField(max_length=1000)
    uploadDate = models.DateTimeField(max_length=100)

class Transcriptions(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    url = models.CharField(max_length=1000)
    name = models.CharField(max_length=1000)
    uploadDate = models.DateTimeField(max_length=100)

class Analysis(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    url = models.CharField(max_length=1000)
    name = models.CharField(max_length=1000)
    uploadDate = models.DateTimeField(max_length=100)

class ThreadTask(models.Model):
    task = models.CharField(max_length=100000, blank=True, null=True)
    is_done = models.BooleanField(blank=False,default=False )