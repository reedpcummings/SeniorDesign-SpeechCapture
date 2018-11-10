# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.template import loader
import boto3
import json
import re
import time
import datetime
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

from .models import Transcription
from django.views.decorators.csrf import csrf_exempt



def index(request):
    return HttpResponse("Hello, world. You're at the homepage index.")

@csrf_exempt
def transcribe(request):
	print (request.body)
	if request.method == 'POST':
		req = json.loads(request.body)
		print ('POST: looking at entries')
		# for entry in request.body:
		# 	print (entry)
		for key in req:
			print (key),
			print (req[key])
			if key == 'fileName':
				# print ('fileName')
				# fileName = request.POST['fileName']
				fileName = req[key]
				now = datetime.datetime.now()
				# job_name = str(now)
				# job_name = re.sub('\.wav$', '', fileName)
				job_name = fileName
				job_uri = "https://s3-us-west-2-amazonaws.com/sa-doc-upload/" + fileName
				newFileName = fileName.replace(".wav",".json")

				s3_client = boto3.client('s3')
				transcribe_client = boto3.client('transcribe')
				transcribe_client.start_transcription_job(
					TranscriptionJobName=job_name,
					Media={'MediaFileUri': job_uri},
					MediaFormat='wav',
					LanguageCode='en-US',
					OutputBucketName='sa-doc-upload',
					Settings={'ShowSpeakerLabels': True, 'MaxSpeakerLabels': 2}
			    )
				while True:
					status = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
					if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
						break
					print("Not ready yet...")
					time.sleep(5)

				result = s3_client.get_object(Bucket='sa-doc-upload', Key= (job_name + '.json'))
			    
			    # Read the object (not compressed):
				text = result["Body"].read().decode()
			    
				data = json.loads(text)
				print (data)
	return HttpResponse("Good")


def record(request):
	s3AudioList = []
	s3_client = boto3.client('s3')
	for key in s3_client.list_objects(Bucket='sa-doc-upload')['Contents']:
		if key['Key'][-4:] == '.mp3' or key['Key'][-4:] == '.wav':
			print(key['Key'])
			s3AudioList.append(key['Key'])
	context = {'s3AudioList':s3AudioList}
	return render(request, 'homepage/record_ajax.html', context)
    # return render(request, 'homepage/record_ajax.html')

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

def showAudioFiles(request):
	# s3_client = boto3.client('s3')
	# for key in s3_client.list_objects(Bucket='sa-doc-upload')['Contents']:
	# 	if key['Key'][-4:] == '.mp3' or key['Key'][-4:] == '.wav':
	# 		print(key['Key'])
	return HttpResponse("Good")
