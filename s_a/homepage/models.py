# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class KeyPhrase(models.Model):
	text = models.CharField(max_length = 100)
	count = models.IntegerField(default=0)
	confidence =  models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)#models.DecimalField(4, 2)
	def __str__(self):
		return self.text


class Entity(models.Model):
	text = models.CharField(max_length = 100)
	category = models.CharField(max_length = 100)
	count = models.IntegerField(default=0)
	confidence =  models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
	def __str__(self):
		return self.text

class Language(models.Model):
	name = models.CharField(max_length = 100)
	confidence =  models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)#models.DecimalField(4, 2)
	def __str__(self):
		return self.name

class Sentiment(models.Model):
	name = models.CharField(max_length = 100)
	confidence =  models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)#models.DecimalField(4, 2)
	def __str__(self):
		return self.name

class Transcription(models.Model):
	text = models.CharField(max_length = 1000)
	key_phrases = models.ManyToManyField(KeyPhrase, null = True, blank = True)
	entities = models.ManyToManyField(Entity, null = True, blank = True)
	language = models.ForeignKey(Language, null = True, blank = True, on_delete=models.CASCADE)
	sentiment = models.ForeignKey(Sentiment, null = True, blank = True, on_delete=models.CASCADE)
	def __str__(self):
		return self.text

