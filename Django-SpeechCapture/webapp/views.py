import os, time, json, boto3
import string
import random
import datetime
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, get_user
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt

from .models import Recordings, Transcriptions, Analysis
from .forms import UserForm
from .libs import Analysis

from django.http import HttpResponse


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def index(request):
    directory_old = os.listdir(os.path.join(os.getcwd(), "webapp", "static"))
    directory_new = os.listdir(os.path.join(os.getcwd(), "webapp", "static", "webapp"))
    return render(request, 'webapp/home.html')

def transcript1(request):
    test1 = "test"
    return render(request, 'webapp/transcript.html', {'data': test1})

@csrf_exempt
def upload(request):
    audio_file = request.FILES['audio_test'].read()

    now = datetime.datetime.now()
    now = now.strftime('%Y-%m-%dT%H-%M') + ('-%02d' % (now.microsecond / 10000))
    fileName = "test_audio_" + now + ".wav"

    file = open(fileName, 'wb')
    file.write(audio_file)
    file.close()
    
    key_file = open(os.path.join(os.path.curdir, 'webapp', 'keys.txt'), 'r')
    
    keys = key_file.read()
    key_file.close()
    keys_json = json.loads(keys)

    s3_client = boto3.client('s3',
        aws_access_key_id=keys_json['aws_access_key_id'],
        aws_secret_access_key=keys_json['aws_secret_access_key'],
        region_name='us-west-2')

    s3_client.upload_file(Filename=os.path.join(os.getcwd(), fileName), Bucket='test-speechcapture', Key=fileName)

    os.remove(fileName)

    return HttpResponse(fileName)

@csrf_exempt
def transcript_backend(request, fileName):
    key_file = open(os.path.join(os.path.curdir, 'webapp', 'keys.txt'), 'r')
    
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
    
    #s3_client.upload_file(Filename=os.path.join(os.path.curdir, fileName), Bucket='test-speechcapture', Key=fileName)
    
    now = datetime.datetime.now()
    now = now.strftime('%Y-%m-%dT%H-%M') + ('-%02d' % (now.microsecond / 10000))

    job_name = re.sub('\.wav$', '', fileName)

    newFileName = fileName.replace(".wav",".json")

    print(newFileName + "\n")

    try:
        s3_client.get_object(Bucket='test-speechcapture', Key=newFileName)
    except:
        print("This is an error message!")
        job_uri = "https://s3-us-west-2-amazonaws.com/test-speechcapture/" + fileName
        
        s3_client2.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': job_uri},
            MediaFormat='wav',
            LanguageCode='en-US',
            OutputBucketName='test-speechcapture',
            Settings={'ShowSpeakerLabels': True, 'MaxSpeakerLabels': 2}
        )
        while True:
            status = s3_client2.get_transcription_job(TranscriptionJobName=job_name)
            if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                break
            print("Not ready yet...")
            time.sleep(5)

    result = s3_client.get_object(Bucket='test-speechcapture', Key= (job_name + '.json'))
    
    # Read the object (not compressed):
    text = result["Body"].read().decode()
    
    data = json.loads(text)
    
    test1 = data['results']['transcripts'][0]['transcript']
    

    current_speaker = 'spk_0'
    same_line = 0
    hold = ''

    for l in data['results']['items']:
        try:
            for k in data['results']['speaker_labels']['segments']:
                for j in k['items']:
                    if(j['start_time'] == l['start_time']):
                        if(j['speaker_label'] == current_speaker):
                            if(same_line == 0):
                                hold = current_speaker + ": " + l['alternatives'][0]['content']
                                same_line = 1
                            else:
                                hold = hold + " " + l['alternatives'][0]['content']
                        else:
                            current_speaker = j['speaker_label']
                            hold = hold + '\n\n' + current_speaker + ': ' + l['alternatives'][0]['content']
                        break
            
        except:
            hold = hold + l['alternatives'][0]['content']
            pass
    
    print(hold)
    # for l in data['results']['items']:
    #     print(l['alternatives'][0]['content'])
    #     print('\n')

        

    # for k in data['results']['speaker_labels']['segments']:
    #     print(k['items'][0]['start_time'])
    #     print('\n')

    # for k in data['results']['speaker_labels']['segments']:
    #     for l in k['items']:
    #         print(k['start_time'])
    #         print('\n')

       

    print('\n')

    

    #print(data['results']['speaker_labels']['segments'])
    key_file = open(os.path.join(os.path.curdir, 'webapp', 'keys.txt'), 'r')
    
    keys = key_file.read()
    key_file.close()
    keys_json = json.loads(keys)
    
    s3_client = boto3.client('s3',
                             aws_access_key_id=keys_json['aws_access_key_id'],
                             aws_secret_access_key=keys_json['aws_secret_access_key'],
                             region_name='us-west-2'
                             )

    print(fileName.replace(".wav",".txt"))

    textFileName = fileName.replace(".wav",".txt")

    with open(textFileName, 'w') as text_file:
        print(test1, file=text_file)

    s3_client.upload_file(Filename=os.path.join(os.getcwd(), textFileName), Bucket='test-speechcapture', Key=textFileName, ExtraArgs={'ACL':'public-read'})

    os.remove(textFileName)

    test1 = "<p>" + test1 + "</p>"

    key_file = open(os.path.join(os.path.curdir, 'webapp', 'keys.txt'), 'r')
    
    keys = key_file.read()
    key_file.close()
    keys_json = json.loads(keys)
    
    s3_client = boto3.client('s3',
                             aws_access_key_id=keys_json['aws_access_key_id'],
                             aws_secret_access_key=keys_json['aws_secret_access_key'],
                             region_name='us-west-2'
                             )

    print(fileName.replace(".wav",".txt"))

    textFileName = fileName.replace(".wav",".txt")

    with open(textFileName, 'w') as text_file:
        print(hold, file=text_file)

    s3_client.upload_file(Filename=os.path.join(os.getcwd(), textFileName), Bucket='test-speechcapture', Key=textFileName, ExtraArgs={'ACL':'public-read'})

    os.remove(textFileName)

    hold = """<p>""" + hold + "</p>"

    return HttpResponse(content=hold)

def transcript(request, fileName):
    return render(request, 'webapp/transcript.html', {'fileName': fileName})

@csrf_exempt
def record(request):
    s3AudioList = []
	#s3_client = boto3.client('s3')

    key_file = open(os.path.join(os.path.curdir, 'webapp', 'keys.txt'), 'r')
    
    keys = key_file.read()
    key_file.close()
    keys_json = json.loads(keys)

    s3_client = boto3.client('s3',
                             aws_access_key_id=keys_json['aws_access_key_id'],
                             aws_secret_access_key=keys_json['aws_secret_access_key'],
                             region_name='us-west-2'
                             )
    
    for key in s3_client.list_objects(Bucket='test-speechcapture')['Contents']:
	    if key['Key'][-4:] == '.mp3' or key['Key'][-4:] == '.wav':
		    print(key['Key'])
		    s3AudioList.append(key['Key'])
    context = {'s3AudioList':s3AudioList}
    return render(request, 'webapp/record.html', context)
    #return render(request, 'webapp/record.html')

@csrf_exempt
def analysis(request):
    f = open("webapp/libs/testinterview.txt", 'r')
    content = f.read()
    entityDict = Analysis.GetAllAttributesV2(content)
    return render(request, 'webapp/analysis.html', {'data': entityDict})

def history(request):
    request.user = get_user(request)
    if request.user.username:
        recs = Recordings.objects.filter(user=request.user.username)
        trans = Recordings.objects.filter(user=request.user.username)
        comps = Recordings.objects.filter(user=request.user.username)
    return render(request, 'webapp/history.html')

class UserFormView(View):
    form_class = UserForm
    template_name = 'webapp/register.html'

    # Display form
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    # Process form
    @csrf_exempt
    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            # Cleaned Data
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user.username = username
            user.set_password(password)
            user.save()

            # Return objects if credentials are correct
            user = authenticate(username=username, password=password)

            # Login the user
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('/')
        # Login failed
        return render(request, self.template_name, {'form': form})
