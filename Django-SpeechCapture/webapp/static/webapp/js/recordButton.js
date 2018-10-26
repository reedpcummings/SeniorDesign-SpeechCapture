var recordButton, stopButton, recorder, clearButton, gotoTranscribeButton;

window.onload = function () {
  recordButton = document.getElementById('record');
  stopButton = document.getElementById('stop');
  clearButton = document.getElementById('clear');
  gotoTranscribeButton = document.getElementById('gotoTranscribeButton');
  gotoTranscribeButton.disabled = true;
  // document.getElementById('audio').controls = false;


  // get audio stream from user's mic
  navigator.mediaDevices.getUserMedia({
    audio: true
  })
  .then(function (stream) {
    recordButton.disabled = false;
    recordButton.addEventListener('click', startRecording);
    stopButton.addEventListener('click', stopRecording);
    clearButton.addEventListener('click', function(e) { clearRecording(e, stream)});
    recorder = new MediaRecorder(stream);

    // listen to dataavailable, which gets triggered whenever we have
    // an audio blob available
    recorder.addEventListener('dataavailable', onRecordingReady);
  });
};

function startRecording() {
  recordButton.disabled = true;
  stopButton.disabled = false;
  clearButton.disabled = true;

  recorder.start();
}

function stopRecording() {
  recordButton.disabled = false;
  stopButton.disabled = true;
  clearButton.disabled = false;
  gotoTranscribeButton.disabled = false;
  // Stopping the recorder will eventually trigger the `dataavailable` event and we can complete the recording process
  recorder.stop();


}

function clearRecording(e, stream) {
  recordButton.disabled = false;
  stopButton.disabled = true;
  clearButton.disabled = true;
  var audio = document.getElementById('audio');
  console.log(stream.getTracks().length);
  const tracks = stream.getTracks();
  // for (track in ) {
  //   console.log(typeof track)
  //   stream.removeTrack(track);
  // }
  stream.removeTrack(tracks[0])
  

  
  console.log(stream.getTracks().length);
  location.reload()
  // stream.removeTrack(stream.getTrackById(0))

  // audio.removeChild(audio.ch)
  // recorder = new MediaRecorder(stream);
  // audio = null;
  // recorder = null;
  // delete recorder;
  // recorder = new MediaRecorder(stream);
  // stream.getTracks() // get all tracks from the MediaStream
  // .forEach( track => track.stop() ); // stop each of them

}

function onRecordingReady(e) {
  var audio = document.getElementById('audio');
  // e.data contains a blob representing the recording
  audio.src = URL.createObjectURL(e.data);
  // audio.play();
}