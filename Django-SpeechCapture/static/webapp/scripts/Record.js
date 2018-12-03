var modified = false;

window.onbeforeunload = s => modified ? "" : null;

function on() { document.getElementById("overlay").style.display = "block"; }
function off() { document.getElementById("overlay").style.display = "none"; }

//webkitURL is deprecated but nevertheless
URL = window.URL || window.webkitURL;

var gumStream; 						//stream from getUserMedia()
var rec; 							//Recorder.js object
var input; 							//MediaStreamAudioSourceNode we'll be recording

// shim for AudioContext when it's not avb. 
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext //audio context to help us record

var recordButton = document.getElementById("recordButton");
var stopButton = document.getElementById("stopButton");
var pauseButton = document.getElementById("pauseButton");

var canvas = document.querySelector('.visualizer');
var mainSection = document.querySelector('.main-controls');
var audioCtx = new(window.AudioContext || webkitAudioContext)();
var canvasCtx = canvas.getContext("2d");

//add events to those 2 buttons
recordButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);
pauseButton.addEventListener("click", pauseRecording);

uploadExistingFileButton.addEventListener("click", uploadExistingFile);
transcribeButton.addEventListener("click", transcribeFile);
//stopButton.addEventListener("click", transcribeFile);

function transcribeFile() {
    var select = document.getElementById("s3-file-select");

    if (select.selectedIndex == -1 || select.options[select.selectedIndex].text == '--Please choose an option--')
        return alert("Please select a valid file from the dropdown.");
    var fName = {'fileName' : select.options[select.selectedIndex].text}
    //alert("Transcribing " + select.options[select.selectedIndex].text)
	location.href = "http://localhost:8000/transcript/" + select.options[select.selectedIndex].text;
	//document.getElementById("transcribeLink").href="http://localhost:8000/transcript/" + select.options[select.selectedIndex].text;

	// $.ajax({
    //     url: 'http://localhost:8000/homepage/transcribe/',
    //     type: 'POST',
    //     data: JSON.stringify(fName),
    //     processData: false,
    //     contentType: "application/json; charset=utf-8",
    //     success: function (data) {
    //         console.log('successfully transcribed' + (data));
    //     },
    //     error: function () {
    //         console.log("you dun messed up")
    //     }
    // });

}

function uploadExistingFile() {

    var files = document.getElementById('file').files;
    if (!files.length) {
        return alert('Please choose a file to upload first.');
    }
    var file = files[0];

    //AJAX upload BLOB
    var form = new FormData();
    form.append('audio_test', file);
	on();
    $.ajax({
		url: 'http://localhost:8000/upload/',
        //url: 'http:local/upload/',
        type: 'POST',
        data: form,
        processData: false,
		contentType: false,
		crossDomain:true,
		headers: {
			'Access-Control-Allow-Origin': '*'
		},
		xhrFields: {
			withCredentials: false
		  },
        success: function (data) {
			off();
			console.log('response' + (data));
            fName = file.name;
            console.log(fName);
            var dropdown = document.getElementById("s3-file-select");

            // give the option a random tag (ie, current date)
            var option = document.createElement('option');
            option.text = data;
            dropdown.add(option);

            for (var i = 0; i < dropdown.options.length; i++) {
                if (dropdown.options[i].text === data) {
                    dropdown.selectedIndex = i;
                    break;
                }
			}
			//document.getElementById("transcribeLink").href="http://localhost:8000/transcript/" + data;
        },
        error: function () {
            console.log("you dun messed up")
        }
    });
}

navigator.mediaDevices.getUserMedia({ audio: true, video:false }).then(function(stream){visualize(stream);});


function startRecording() {
	modified = true;
	console.log("recordButton clicked");
	/*
		Simple constraints object, for more advanced audio features see
		https://addpipe.com/blog/audio-constraints-getusermedia/
	*/
    
    var constraints = { audio: true, video:false }

 	/*
    	Disable the record button until we get a success or fail from getUserMedia() 
	*/

	recordButton.disabled = true;
	stopButton.disabled = false;
	pauseButton.disabled = false

	/*
    	We're using the standard promise based getUserMedia() 
    	https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia
	*/

	navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
		console.log("getUserMedia() success, stream created, initializing Recorder.js ...");

		/*
			create an audio context after getUserMedia is called
			sampleRate might change after getUserMedia is called, like it does on macOS when recording through AirPods
			the sampleRate defaults to the one set in your OS for your playback device

		*/
		audioContext = new AudioContext();

		//update the format 
		document.getElementById("formats").innerHTML="Format: 1 channel pcm @ "+audioContext.sampleRate/1000+"kHz"

		/*  assign to gumStream for later use  */
		gumStream = stream;
        
        //visualize(stream)
        
		/* use the stream */
		input = audioContext.createMediaStreamSource(stream);

		/* 
			Create the Recorder object and configure to record mono sound (1 channel)
			Recording 2 channels  will double the file size
		*/
		rec = new Recorder(input,{numChannels:1})

		//start the recording process
		rec.record()

        console.log("Recording started");
        
        

	}).catch(function(err) {
	  	//enable the record button if getUserMedia() fails
    	recordButton.disabled = false;
    	stopButton.disabled = true;
    	pauseButton.disabled = true
    });
    

    
    
    //visualize(stream)
}

function pauseRecording(){
	console.log("pauseButton clicked rec.recording=",rec.recording );
	if (rec.recording){
		//pause
		rec.stop();
		pauseButton.innerHTML="Resume";
	}else{
		//resume
		rec.record()
		pauseButton.innerHTML="Pause";

	}
}

function stopRecording() {
	console.log("stopButton clicked");

	//disable the stop button, enable the record too allow for new recordings
	stopButton.disabled = true;
	recordButton.disabled = false;
	pauseButton.disabled = true;

	//reset button just in case the recording is stopped while paused
	pauseButton.innerHTML="Pause";
	
	//tell the recorder to stop the recording
	rec.stop();

	//stop microphone access
	gumStream.getAudioTracks()[0].stop();

	//create the wav blob and pass it on to createDownloadLink
    rec.exportWAV(createDownloadLink);
	
	///////////////////////////////////////////////////////////////////////////////////////////////////

	//rec.exportWAV(upload);
	
	//////////////////////////////////////////////////////////////////////////////////////////////////
}

function createDownloadLink(blob) {
	
	var url = URL.createObjectURL(blob);
	var au = document.createElement('audio');
	var li = document.createElement('li');
	var link = document.createElement('a');

	//name of .wav file to use during upload and download (without extendion)
	var filename = new Date().toISOString();

	//add controls to the <audio> element
	au.controls = true;
	au.src = url;

	//save to disk link
	link.href = url;
	link.download = filename+".wav"; //download forces the browser to donwload the file using the  filename
	link.innerHTML = "Save to disk";

	//add the new audio element to li
	li.appendChild(au);
	
	//add the filename to the li
	li.appendChild(document.createTextNode(filename+".wav "))

	/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	//document.getElementById("transcribeLink").href="localhost:8000/transcript/" + filename + ".wav"; 
	//$('#transcribeLink').attr('href',"http://localhost:8000/transcript/" + filename + ".wav");
	////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

	//add the save to disk link to li
	li.appendChild(link);
	
	//upload link
	var upload = document.createElement('a');
	upload.href="#";
	upload.innerHTML = "Upload";
	// upload.addEventListener("click", function(event){
	// 	  var xhr=new XMLHttpRequest();
	// 	  xhr.onload=function(e) {
	// 	      if(this.readyState === 4) {
	// 	          console.log("Server returned: ",e.target.responseText);
	// 	      }
	// 	  };
	// 	  var fd=new FormData();
	// 	  fd.append("audio_data",blob, filename);
	// 	  xhr.open("POST","upload.php",true);
	// 	  xhr.send(fd);
	// })
	

	upload.addEventListener("click", function(event){
		
		// var blob = new File([blob], filename+".mp3 ");
	
		// console.log('after conversion')
		// console.log (blob.size)
		//AJAX upload BLOB
	
		var form = new FormData();
		on();
		// form.append('audio_test', blob, filename + ".wav");
		form.append('audio_test', blob);
	
		$.ajax({
			//url: 'http://django-env.krxijs76pr.us-west-2.elasticbeanstalk.com/upload/',
			url: 'http://localhost:8000/upload/',
			type: 'POST',
			data: form,
			processData: false,
			contentType: false,
			crossDomain:true,
			success: function (data) {
				off();
				console.log('response ' + (data));
				var dropdown = document.getElementById("s3-file-select");
	
				// give the option a random tag (ie, current date)
				var option = document.createElement('option');
				option.text = data;
				dropdown.add(option);
	
				for (var i = 0; i < dropdown.options.length; i++) {
					if (dropdown.options[i].text === data) {
						dropdown.selectedIndex = i;
						break;
					}
				}
				modified = false;
				//console.log('response' + " " + (data));
            	//document.getElementById("transcribeLink").href="http://localhost:8000/transcript/" + data;
			},
			error: function () {
				console.log("you dun messed up")
			}
		});
	
	
	});

	li.appendChild(document.createTextNode (" "))//add a space in between
	li.appendChild(upload)//add the upload link to li

	//add the li element to the ol
	recordingsList.appendChild(li);
}

function visualize(stream) {
    var source = audioCtx.createMediaStreamSource(stream);

    var analyser = audioCtx.createAnalyser();
    analyser.fftSize = 2048;
    var bufferLength = analyser.frequencyBinCount;
    var dataArray = new Uint8Array(bufferLength);

    source.connect(analyser);
    //analyser.connect(audioCtx.destination);

    draw()

    function draw() {
        WIDTH = canvas.width
        HEIGHT = canvas.height;

        requestAnimationFrame(draw);

        analyser.getByteTimeDomainData(dataArray);

        canvasCtx.fillStyle = 'rgb(200, 200, 200)';
        canvasCtx.fillRect(0, 0, WIDTH, HEIGHT);

        canvasCtx.lineWidth = 2;
        canvasCtx.strokeStyle = 'rgb(0, 0, 0)';

        canvasCtx.beginPath();

        var sliceWidth = WIDTH * 1.0 / bufferLength;
        var x = 0;


        for (var i = 0; i < bufferLength; i++) {

            var v = dataArray[i] / 128.0;
            var y = v * HEIGHT / 2;

            if (i === 0) {
                canvasCtx.moveTo(x, y);
            } else {
                canvasCtx.lineTo(x, y);
            }

            x += sliceWidth;
        }

        canvasCtx.lineTo(canvas.width, canvas.height / 2);
        canvasCtx.stroke();

    }
}