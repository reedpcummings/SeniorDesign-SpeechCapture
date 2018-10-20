from django.contrib import admin
from .models import Recordings
from .models import Transcriptions
from .models import Analysis

admin.site.register(Recordings)
admin.site.register(Transcriptions)
admin.site.register(Analysis)