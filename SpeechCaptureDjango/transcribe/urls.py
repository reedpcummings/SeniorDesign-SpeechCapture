from django.urls import path
from . import views

urlpatterns = [
    path('record2/', views.record2, name='record2'),
    path('fileHandle/', views.fileHandle, name='fileHandle'),
    path('record/', views.record, name='record'),
    path('<fileName>/', views.index, name='index'),
    path('', views.index, name='index'),
]
