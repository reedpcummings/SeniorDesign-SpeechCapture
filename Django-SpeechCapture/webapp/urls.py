from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    url('^$', views.index, name='index'),
    path('transcript/', views.transcript_default, name='transcript'),
    path('transcript/<fileName>/', views.transcript, name='transcript_default'),
    path('analysis/<fileName>/', views.analysis, name='analysis'),
    path('analysis', views.analysis_default, name='analysis'),
    path('startThreadTask/<fileName>/', views.startThreadTask, name='startThreadTask'),
    #path('startThreadTask/', views.startThreadTask, name='startThreadTask'),
    url(r'^checkThreadTask/(?P<id>[0-9]+)/?$',views.checkThreadTask, name='checkThreadTask'),
    url('^record/', views.record, name='record'),
    #path('transcript_backend/<fileName>/', views.transcript_backend),
    #path('transcript_backend/', views.transcript),
    path('upload/', views.upload)
]
