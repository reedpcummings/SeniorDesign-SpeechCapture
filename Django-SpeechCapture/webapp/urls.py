from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    url('^$', views.index, name='index'),
    url('register/', views.UserFormView.as_view(), name='register'),
    path('transcript/', views.transcript_default, name='transcript'),
    path('transcript/<fileName>/', views.transcript, name='transcript_default'),
    path('analysis/<fileName>/', views.analysis, name='analysis'),
    url('^record/', views.record, name='record'),
    url('^hist/', views.history, name='history'),
    path('transcript_backend/<fileName>/', views.transcript_backend),
    path('transcript_backend/', views.transcript),
    path('upload/', views.upload)
]
