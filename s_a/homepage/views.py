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



	# for t in latest_transcription_list:

	# 	output = str(t.id) + "\n\tTEXT: " + ', '.join([t.text])
	# 	output += '\n\t\t' + str(t.key_phrases)
	# 	output += '\n\t\t\t' + str(t.language)
	# 	output += '\n\t\t\t\t' + str(t.sentiment)
	# return HttpResponse(output)
	#response = "You're looking at the results of transcription %s."
	#return HttpResponse(response % transcription_id)
# Create your views here.

