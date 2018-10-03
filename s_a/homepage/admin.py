# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import *

from django.contrib import admin

# Register your models here.
admin.site.register(KeyPhrase)
admin.site.register(Entity)
admin.site.register(Sentiment)
admin.site.register(Language)
admin.site.register(Transcription)