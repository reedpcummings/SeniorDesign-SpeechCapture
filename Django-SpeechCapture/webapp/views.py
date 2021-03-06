import threading
import os, time, json, boto3
import string
import datetime
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, get_user
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt

from .models import Recordings, Transcriptions, Analysis, ThreadTask
from .forms import UserForm
from .libs import Analysis

from django.http import HttpResponse

bucket_name = 'test-speechcapture'

def index(request):
    return render(request, 'webapp/home.html')

def transcript_default(request):
    # content = ""
    s3AudioList = [] #will be the list of files that are stored in S3, will be in the dropdown on the record page

    #open the file that contains the AWS access keys
    key_file = open(os.path.join(os.path.curdir, 'webapp', 'keys.txt'), 'r')
    
    #read the contents of the AWS keys file then close it
    keys = key_file.read()
    key_file.close()
    
    #load the keys to to json so each key can be accessed easier
    keys_json = json.loads(keys)

    #connect to AWS S3 using boto3 and the AWS keys loaded from the file
    s3_client = boto3.client('s3',
                             aws_access_key_id=keys_json['aws_access_key_id'],
                             aws_secret_access_key=keys_json['aws_secret_access_key'],
                             region_name='us-west-2'
                             )
    
    #iterate through files in S3
    # for key in s3_client.list_objects(Bucket='test-speechcapture')['Contents']:
       #  if key['Key'][-4:] == '.mp3' or key['Key'][-4:] == '.wav': #if the file is a wav or mp3
          #   print(key['Key']) #log(print) the file name
          #   s3AudioList.append(key['Key']) #append the name of the audio file to the list
    for key in s3_client.list_objects(Bucket=bucket_name)['Contents']:
        if key['Key'][-4:] == '.mp3' or key['Key'][-4:] == '.wav': #if the file is a wav or mp3
            #print(key['Key']) #log(print) the file name
            s3AudioList.append(key['Key']) #append the name of the audio file to the list
    
    #render the record page and pass into the page the list of files we found in S3
    context = {'s3AudioList':s3AudioList}
    # return render(request, 'webapp/transcript.html', {'data': content})
    return render(request, 'webapp/transcript.html', context)

@csrf_exempt
@never_cache
def upload(request):
    audio_file = request.FILES['audio_test'].read() #get the audio file from the POST passed in (request)
    now = datetime.datetime.now() #get current date/time
    now = now.strftime('%Y-%m-%d-T%H-%M') + ('-%02d' % (now.microsecond / 10000)) #put into format we want
    audioFileName = request.FILES['audio_test'].name.replace('.wav', '')
    fileName = audioFileName + "_" + now + ".wav" #create the file name that includes the date/time as well as the file extension(in this case .wav)

    #open the file to be written with name fileName, write the audio to that file, close the file
    file = open(fileName, 'wb')
    file.write(audio_file)
    file.close()
    
    #open the file that contains the AWS access keys
    key_file = open(os.path.join(os.path.curdir, 'webapp', 'keys.txt'), 'r')
    
    #read the contents of the AWS keys file then close it
    keys = key_file.read()
    key_file.close()
    
    #load the keys to to json so each key can be accessed easier
    keys_json = json.loads(keys)

    #connect to AWS S3 using boto3 and the AWS keys loaded from the file 
    s3_client = boto3.client('s3',
        aws_access_key_id=keys_json['aws_access_key_id'],
        aws_secret_access_key=keys_json['aws_secret_access_key'],
        region_name='us-west-2')

    #upload the audio file we created to S3 
    s3_client.upload_file(Filename=os.path.join(os.getcwd(), fileName), Bucket=bucket_name, Key=fileName)

    #update databse
    recording_model = Recordings()
    recording_model.name = fileName
    recording_model.uploadDate = datetime.datetime.now()
    recording_model.url = "https://" + bucket_name + ".s3.amazonaws.com/" + fileName
    recording_model.save()

    #remove the file from the local file system
    os.remove(fileName)

    #return the file name so that we can display that name on the webpage
    return HttpResponse(fileName)

@never_cache
def startThreadTask(request, fileName):
    task = ThreadTask()
    task.save()
    t = threading.Thread(target=transcript_backend,args=[fileName, task.id])
    t.setDaemon(True)
    t.start()
    check = "Original task: " + str(task.id)
    return JsonResponse({'id':task.id, 'check':check})

@never_cache
def checkThreadTask(request,id):
    #open the file that contains the AWS access keys
    key_file = open(os.path.join(os.path.curdir, 'webapp', 'keys.txt'), 'r')
    
    #read the contents of the AWS keys file then close it
    keys = key_file.read()
    key_file.close()
    
    #load the keys to to json so each key can be accessed easier
    keys_json = json.loads(keys)
    
    #connect to AWS S3 using boto3 and the AWS keys loaded from the file
    s3_client = boto3.client('s3',
                             aws_access_key_id=keys_json['aws_access_key_id'],
                             aws_secret_access_key=keys_json['aws_secret_access_key'],
                             region_name='us-west-2'
                             )
    task = ThreadTask.objects.get(pk=id)

    if(task.is_done):
        print("Finished Properly")
        result = {}
        result['is_done'] = task.is_done
        result['result'] = task.task
        return JsonResponse(result)
        #return JsonResponse({'is_done':task.is_done, 'result':task.task})
    else:
        return JsonResponse({'is_done':task.is_done})

    # try:
    #     s3_client.get_object(Bucket='test-speechcapture', Key=newFileName)
        
        
    #         print("Finished Parsing")
    #         print("Task: " + task.task)
    #         return JsonResponse({'is_done':task.is_done, 'result':task.task})
    # except:
    #         return JsonResponse({'is_done':task.is_done})

######################################################################################################################
# The backend of the transcription page.                                                                             #
# Handles the transcription of the file in S3 whose name is passed in(fileName) and returns the transcription result.#
######################################################################################################################
@csrf_exempt
@never_cache
def transcript_backend(fileName, id):
    task = ThreadTask.objects.get(pk=id)

    #open the file that contains the AWS access keys
    key_file = open(os.path.join(os.path.curdir, 'webapp', 'keys.txt'), 'r')
    
    #read the contents of the AWS keys file then close it
    keys = key_file.read()
    key_file.close()
    
    #load the keys to to json so each key can be accessed easier
    keys_json = json.loads(keys)
    
    #connect to AWS S3 using boto3 and the AWS keys loaded from the file
    s3_client = boto3.client('s3',
                             aws_access_key_id=keys_json['aws_access_key_id'],
                             aws_secret_access_key=keys_json['aws_secret_access_key'],
                             region_name='us-west-2'
                             )
    
    #connect to AWS Transcribe using boto3 and the AWS keys loaded from the file
    transcribe_client = boto3.client('transcribe',
                              aws_access_key_id=keys_json['aws_access_key_id'],
                              aws_secret_access_key=keys_json['aws_secret_access_key'],
                              region_name='us-west-2'
                              )

    now = datetime.datetime.now() #get the current date/time
    now = now.strftime('%Y-%m-%dT%H-%M') + ('-%02d' % (now.microsecond / 10000)) #format the date/time

    job_name = re.sub('\.wav$', '', fileName) #remove the .wav part of the fileName passed in

    newFileName = fileName.replace(".wav",".json") #replace .wav with .json in the fileName and save that as a seperate variable (this will be used for checking if the transcription has already been done before and in getting the output of the transcription as this will be the name of the file Transcribe outputs)

    #try to get the file in S3 named newFileName which is the normal fileName with .json at the end instead of .wav
    #if it doesn't find the file it will throw an exception and we will go to the except and run that
    try:
        s3_client.get_object(Bucket=bucket_name, Key=newFileName)
    #file is not found so the transcription is not readily available thus we need to create the transcription job
    except:
        print("Transcription not already performed. Starting new transcription.") #log that a new transcription is being done
        job_uri = "http://s3-us-west-2-amazonaws.com/" + bucket_name + "/" + fileName #URL to the audio file we wish to transcribe (will be passed to AWS Transcribe)
        
        #start the new transcription job
        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name, #name of the job
            Media={'MediaFileUri': job_uri}, #the URL of the audio file is passed in
            MediaFormat='wav', #the file type of the audio file
            LanguageCode='en-US', #language of the audio file
            OutputBucketName=bucket_name, #the S3 bucket to output the transcription file to(the file will be the same name as the job_name appended with .json)
            Settings={'ShowSpeakerLabels': True, 'MaxSpeakerLabels': 2} #allow speaker identification with a max number of speakers being 2
        )

        time_elapsed = 0 #will be used to log how long the transcription takes

        #Now that the transcription job is in progress we need to constantly check whether it is finished
        while True:
            status = transcribe_client.get_transcription_job(TranscriptionJobName=job_name) #get the status of the transcription job
            
            #check if the transcription job has completed or failed, if so break the loop
            if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                break
            
            print(time_elapsed) #print the time_elapsed so that we can log how long the transcription takes
            time_elapsed = time_elapsed + 5 #add the number of seconds we will wait between status checks
            time.sleep(5) #time to wait between status checks of the transcription job, in our case it is 5 seconds

    #get the transcript of the audio file from the S3 bucket (will be a json file)
    result = s3_client.get_object(Bucket=bucket_name, Key= newFileName)
    
    #read the Body of the json and decode it so we can access the contents
    text = result["Body"].read().decode()
    
    #load the text with the json library to make it easier to access the contents of the json file
    data = json.loads(text)
    
    #will be the raw transcript of the audio with no speaker identification, just in a paragraph
    transcription = data['results']['transcripts'][0]['transcript']
    
    #This next section is parsing the json, that has speaker identification, and printing the conversation in order
    current_speaker = 'spk_0' #used to determine if speaker has changed, starts with speaker 0
    same_line = 0 #used to determine if we are on the same line (used like a boolean)
    hold = '' #will hold the final text

    #the actual parsing
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
            
        except: #if there is an error (like not having a certain section) then it must be a punctuation
            hold = hold + l['alternatives'][0]['content'] #get the alternative
            pass #go to next iteration
    
    print(hold + '\n') #log the output of our parsing 

    textFileName = fileName.replace(".wav",".txt") #the name of our text file that will contain our transcript, for easy download and also for use with AWS Comprehend

    #open the text file and write our transcript to it
    with open(textFileName, 'w') as text_file:
        print(hold, file=text_file)

    #upload the text file to S3
    s3_client.upload_file(Filename=os.path.join(os.getcwd(), textFileName), Bucket=bucket_name, Key=textFileName, ExtraArgs={'ACL':'public-read'})



    # update database
    transcript_model = Transcriptions()
    transcript_model.name = fileName
    transcript_model.uploadDate = datetime.datetime.now()
    transcript_model.url = "https://" + bucket_name + ".s3.amazonaws.com/" + textFileName
    transcript_model.save()

    os.remove(textFileName) #remove the file from the local machine now that it has been uploaded

    hold = """<p>""" + hold + "</p>" #add html tags to our transcription so that when we return it we can print it in the browser

    task.task = hold
    task.is_done = True
    task.save()

@never_cache
def transcript(request, fileName):
    s3AudioList = [] #will be the list of files that are stored in S3, will be in the dropdown on the record page

    #open the file that contains the AWS access keys
    key_file = open(os.path.join(os.path.curdir, 'webapp', 'keys.txt'), 'r')
    
    #read the contents of the AWS keys file then close it
    keys = key_file.read()
    key_file.close()
    
    #load the keys to to json so each key can be accessed easier
    keys_json = json.loads(keys)
    
    #connect to AWS S3 using boto3 and the AWS keys loaded from the file
    s3_client = boto3.client('s3',
                             aws_access_key_id=keys_json['aws_access_key_id'],
                             aws_secret_access_key=keys_json['aws_secret_access_key'],
                             region_name='us-west-2'
                             )
    
    #iterate through files in S3
    # for key in s3_client.list_objects(Bucket='test-speechcapture')['Contents']:
       #  if key['Key'][-4:] == '.mp3' or key['Key'][-4:] == '.wav': #if the file is a wav or mp3
          #   print(key['Key']) #log(print) the file name
          #   s3AudioList.append(key['Key']) #append the name of the audio file to the list
    for key in s3_client.list_objects(Bucket=bucket_name)['Contents']:
        if key['Key'][-4:] == '.mp3' or key['Key'][-4:] == '.wav': #if the file is a wav or mp3
            #print(key['Key']) #log(print) the file name
            s3AudioList.append(key['Key']) #append the name of the audio file to the list
    
    #render the record page and pass into the page the list of files we found in S3
    context = {'s3AudioList':s3AudioList}
    context['fileName'] = fileName
    # return render(request, 'webapp/transcript.html', {'fileName': fileName})
    return render(request, 'webapp/transcript.html', context)

@csrf_exempt
def record(request):
    s3AudioList = [] #will be the list of files that are stored in S3, will be in the dropdown on the record page

    #open the file that contains the AWS access keys
    key_file = open(os.path.join(os.path.curdir, 'webapp', 'keys.txt'), 'r')
    
    #read the contents of the AWS keys file then close it
    keys = key_file.read()
    key_file.close()
    
    #load the keys to to json so each key can be accessed easier
    keys_json = json.loads(keys)
    
    #connect to AWS S3 using boto3 and the AWS keys loaded from the file
    s3_client = boto3.client('s3',
                             aws_access_key_id=keys_json['aws_access_key_id'],
                             aws_secret_access_key=keys_json['aws_secret_access_key'],
                             region_name='us-west-2'
                             )
    
    #iterate through files in S3
    for key in s3_client.list_objects(Bucket=bucket_name)['Contents']:
        if key['Key'][-4:] == '.mp3' or key['Key'][-4:] == '.wav': #if the file is a wav or mp3
		    #print(key['Key']) #log(print) the file name
            s3AudioList.append(key['Key']) #append the name of the audio file to the list
    
    #render the record page and pass into the page the list of files we found in S3
    context = {'s3AudioList':s3AudioList}
    return render(request, 'webapp/record.html', context)
    
def analysis_default(request):
    s3TextList = []  # list of all txt files in s3
    # open the file that contains the AWS access keys
    key_file = open(os.path.join(os.path.curdir, 'webapp', 'keys.txt'), 'r')

    # read the contents of the AWS keys file then close it
    keys = key_file.read()
    key_file.close()

    # load the keys to to json so each key can be accessed easier
    keys_json = json.loads(keys)

    # connect to AWS S3 using boto3 and the AWS keys loaded from the file
    s3_client = boto3.client('s3',
                             aws_access_key_id=keys_json['aws_access_key_id'],
                             aws_secret_access_key=keys_json['aws_secret_access_key'],
                             region_name='us-west-2'
                             )

    for key in s3_client.list_objects(Bucket=bucket_name)['Contents']:
        if key['Key'][-4:] == '.txt':  # if the file is txt
            s3TextList.append(key['Key'])  # append the name of the audio file to the list

    # render the record page and pass into the page the list of files we found in S3
    context = {'s3TextList': s3TextList}
    # return render(request, 'webapp/transcript.html', {'data': content})
    return render(request, 'webapp/analysis.html', context)

@csrf_exempt
def analysis(request, fileName):
    s3TextList = []  # list of all txt files in s3
    key_file = open(os.path.join(os.path.curdir, 'webapp', 'keys.txt'), 'r')

    keys = key_file.read()
    key_file.close()
    keys_json = json.loads(keys)

    s3_client = boto3.client('s3',
                             aws_access_key_id=keys_json['aws_access_key_id'],
                             aws_secret_access_key=keys_json['aws_secret_access_key'],
                             region_name='us-west-2'
                             )

    for key in s3_client.list_objects(Bucket=bucket_name)['Contents']:
        if key['Key'][-4:] == '.txt':  # if the file is txt
            s3TextList.append(key['Key'])  # append the name of the audio file to the list

    job_name = fileName.replace(".txt","") #re.sub('\.txt$', '', fileName)
    # If the file already exists in the bucket
    key_name = (job_name + 'Analysis' + '.json')
    try:
        result = s3_client.get_object(Bucket=bucket_name, Key=(key_name))
    except:
        result = s3_client.get_object(Bucket=bucket_name, Key=(fileName))
        text = result["Body"].read().decode()
        Analysis.GetAllAttributesV2(text, fileName)
        # wait for the file to be uploaded to the bucket
        while True:
            try:
                result = s3_client.get_object(Bucket=bucket_name, Key=(key_name))
                break
            except:
                print("Not ready yet...")
                time.sleep(5)
    text = result["Body"].read().decode()
    result = json.loads(text)
    return render(request, 'webapp/analysis.html', {'data': result, 's3TextList': s3TextList})