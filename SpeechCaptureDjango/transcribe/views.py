from django.shortcuts import render
from django.http import HttpResponse
import boto3
import json
import os

# Create your views here.
def index(request):    
    key_file = open(os.path.join(os.path.curdir, 'transcribe', 'keys.txt'), 'r')

    keys = key_file.read()
    key_file.close()
    keys_json = json.loads(keys)

    s3_client = boto3.client('s3', 
                aws_access_key_id=keys_json['aws_access_key_id'], 
                aws_secret_access_key=keys_json['aws_secret_access_key'], 
                region_name='us-west-2'
                )

#     job_uri = "https://s3-us-west-2-amazonaws.com/test-speechcapture/09_14_Test10.wav"
#     s3_client.start_transcription_job(
#     TranscriptionJobName='Test58',
#     Media={'MediaFileUri': job_uri},
#     MediaFormat='wav',
#     LanguageCode='en-US',
#     OutputBucketName='test-speechcapture'
# )
    test = "Test"
    result = s3_client.get_object(Bucket='test-speechcapture', Key='09_14_Test10.json')
 
    # Read the object (not compressed):
    text = result["Body"].read().decode()

 
    data = json.loads(text)

    test1 = data['results']['transcripts'][0]['transcript']

    #json_file.close()

    return render(request, 'transcribe/index.html', {'data': test, 'test1':test1})
    #HttpResponse("<h1>This is a test <button>Click Me!</button>")
