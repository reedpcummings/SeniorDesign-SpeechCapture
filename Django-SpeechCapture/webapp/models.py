from django.db import models
from django.conf import settings


class Recordings(models.Model):
    url = models.CharField(max_length=1000)
    name = models.CharField(max_length=1000)
    uploadDate = models.DateTimeField(max_length=100)


class Transcriptions(models.Model):
    url = models.CharField(max_length=1000)
    name = models.CharField(max_length=1000)
    uploadDate = models.DateTimeField(max_length=100)


class Analysis(models.Model):
    url = models.CharField(max_length=1000)
    name = models.CharField(max_length=1000)
    uploadDate = models.DateTimeField(max_length=100)


class ThreadTask(models.Model):
    task = models.CharField(max_length=1000000, blank=True, null=True)
    is_done = models.BooleanField(blank=False, default=False)
