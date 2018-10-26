# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.template import loader
import boto3
import json
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

from .models import Transcription
from django.views.decorators.csrf import csrf_exempt



def index(request):
    return HttpResponse("Hello, world. You're at the homepage index.")


def record(request):
    return render(request, 'homepage/record_ajax.html')

def results(request, transcription_id):
	#comprehend = boto3.client(service_name='comprehend', region_name='us-west-2', aws_access_key_id="", aws_secret_access_key="" )
	comprehend = boto3.client('comprehend')
	text = "It is raining today in Seattle"
	print('Calling DetectDominantLanguage')
	print(json.dumps(comprehend.detect_dominant_language(Text = text), sort_keys=True,
	 indent=4))
	print("End of DetectDominantLanguage\n")
	transList = []
	transcription = Transcription.objects.get(id=transcription_id)
	transList.append(transcription)
	context = {'transList': transList}
	return render(request, 'homepage/index.html', context)

@csrf_exempt
def upload(request):
	audio_file = request.FILES['audio_test'].read()
	file = open('test_audio.wav', 'wb')
	file.write(audio_file)
	file.close()

	audio_name = request.FILES['audio_test'].name
	s3_client = boto3.client('s3')

	s3_client.upload_file(Filename= 'test_audio.wav', Bucket='sa-doc-upload', Key=audio_name)

	return HttpResponse("Good")
