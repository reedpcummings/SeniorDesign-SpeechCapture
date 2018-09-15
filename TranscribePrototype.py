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

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("* recording")

frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()

wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

s3 = boto3.resource('s3')
bucket = s3.Bucket('test-speechcapture')
bucket.upload_file(WAVE_OUTPUT_FILENAME, WAVE_OUTPUT_FILENAME)

transcribe = boto3.client('transcribe')

job_uri = "https://s3-us-west-2-amazonaws.com/test-speechcapture/" + WAVE_OUTPUT_FILENAME
transcribe.start_transcription_job(
    TranscriptionJobName=job_name,
    Media={'MediaFileUri': job_uri},
    MediaFormat='wav',
    LanguageCode='en-US',
    OutputBucketName='test-speechcapture'
)
while True:
    status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
    if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
        break
    print("Not ready yet...")
    time.sleep(5)

bucket.download_file(job_name + '.json', job_name + '.json')

json_file = open(job_name + '.json')
data = json.load(json_file)

print(data['results']['transcripts'][0]['transcript'])

json_file.close()
