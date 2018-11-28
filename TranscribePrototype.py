from __future__ import print_function
import time
import boto3
import botocore
import pyaudio
import wave
import json

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 5
job_name = input("Enter job name: ")
WAVE_OUTPUT_FILENAME = job_name + '.wav'
WAVE_OUTPUT_FILENAME1 = job_name + '1' + '.wav'


p = pyaudio.PyAudio()

########################
info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')
for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print ("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i), "\n")

			
devinfo = p.get_device_info_by_index(1)  # Or whatever device you care about.
if p.is_format_supported(44100.0,  # Sample rate
                         input_device=devinfo['index'],
                         input_channels=devinfo['maxInputChannels'],
                         input_format=pyaudio.paInt16):
	print ('Yay!')
print("Test")
########################

stream = p.open(format=FORMAT,
                channels=1,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
				input_device_index=0)

stream1 = p.open(format=FORMAT,
                channels=1,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
				input_device_index=1)
				
print("* recording")

frames = []
frames1 = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
	data = stream.read(CHUNK)
	frames.append(data)
	data = stream1.read(CHUNK)
	frames1.append(data)
	
print("* done recording")

stream.stop_stream()
stream.close()

stream1.stop_stream()
stream1.close()

p.terminate()

wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

wf = wave.open(WAVE_OUTPUT_FILENAME1, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames1))
wf.close()

# s3 = boto3.resource('s3')
# bucket = s3.Bucket('test-speechcapture')
# bucket.upload_file(WAVE_OUTPUT_FILENAME, WAVE_OUTPUT_FILENAME)

# transcribe = boto3.client('transcribe')

# job_uri = "https://s3-us-west-2-amazonaws.com/test-speechcapture/" + WAVE_OUTPUT_FILENAME
# transcribe.start_transcription_job(
#     TranscriptionJobName=job_name,
#     Media={'MediaFileUri': job_uri},
#     MediaFormat='wav',
#     LanguageCode='en-US',
#     OutputBucketName='test-speechcapture'
# )
# while True:
#     status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
#     if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
#         break
#     print("Not ready yet...")
#     time.sleep(5)

# bucket.download_file(job_name + '.json', job_name + '.json')

# json_file = open(job_name + '.json')
# data = json.load(json_file)

# print(data['results']['transcripts'][0]['transcript'])

# json_file.close()
