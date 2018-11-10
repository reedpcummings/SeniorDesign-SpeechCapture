from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<transcription_id>[0-9]+)/results/$', views.results, name='results'),
    url(r'^record', views.record, name='record'),
    url(r'^upload', views.upload, name='upload'),
    url(r'^getS3', views.showAudioFiles, name='getS3'),
    url(r'^transcribe', views.transcribe, name='transcribe'),
]