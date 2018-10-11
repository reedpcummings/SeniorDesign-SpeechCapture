from django.shortcuts import render
from django.http import HttpResponse
import boto3
import json
import os

###########################################################################################################
from django.views.decorators.csrf import csrf_exempt
###########################################################################################################

# Create your views here.
def index(request, fileName):    
    print("Test")
    key_file = open(os.path.join(os.path.curdir, 'transcribe', 'keys.txt'), 'r')

    keys = key_file.read()
    key_file.close()
    keys_json = json.loads(keys)

    s3_client = boto3.client('s3', 
                aws_access_key_id=keys_json['aws_access_key_id'], 
                aws_secret_access_key=keys_json['aws_secret_access_key'], 
                region_name='us-west-2'
                )

    
    s3_client2 = boto3.client('transcribe', 
                aws_access_key_id=keys_json['aws_access_key_id'], 
                aws_secret_access_key=keys_json['aws_secret_access_key'], 
                region_name='us-west-2'
                )

    s3_client.upload_file(Filename=os.path.join(os.path.curdir, fileName), Bucket='test-speechcapture', Key=fileName)

    job_uri = "https://s3-us-west-2-amazonaws.com/test-speechcapture/" + fileName
    s3_client2.start_transcription_job(
        TranscriptionJobName='Test60',
        Media={'MediaFileUri': job_uri},
        MediaFormat='wav',
        LanguageCode='en-US',
        OutputBucketName='test-speechcapture'
    )
    test = "Test"
    result = s3_client.get_object(Bucket='test-speechcapture', Key='09_14_Test10.json')
 
    # Read the object (not compressed):
    text = result["Body"].read().decode()

    data = json.loads(text)

    test1 = data['results']['transcripts'][0]['transcript']

    #json_file.close()

    test2_file = open(os.path.join(os.path.curdir, 'transcribe', 'test.txt'), 'r')
    test2 = test2_file.read()
    test2_file.close()

    test_file = open(fileName, "r")
    test_file.close()

    return render(request, 'transcribe/index.html', {'test1':test1, 'test2': test2})


@csrf_exempt
def record(request):
    if request.is_ajax():
        message = "Yes, AJAX!"
        print(message)

        if request.method == "POST":
            audio_file = request.FILES['audio_test'].read()
            file = open('test_audio.wav', 'wb')
            file.write(audio_file)
            file.close()

            return index(request)

    else:
        message = "Not Ajax"
        print(message)

    return render(request, 'transcribe/record.html', {})

@csrf_exempt
def fileHandle(request):
    audio_data = request.FILES['audio_test']
    if(audio_data is not None):
        print("Success!")
    else:
        print("Fail")