from django.conf.urls import url
from . import views

urlpatterns = [
    url('^$', views.index, name='index'),
    url('register/', views.UserFormView.as_view(), name='register'),
    url('^transcript/', views.transcript, name='transcript'),
    url('^analysis/', views.analysis, name='analysis'),
    url('^record/', views.record, name='record'),
    url('^hist/', views.history, name='history'),
]
