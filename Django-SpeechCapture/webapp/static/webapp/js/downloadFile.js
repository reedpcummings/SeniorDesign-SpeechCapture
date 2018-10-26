function download(text, name, type) {
	var a = document.getElementById("saveButton");
	var file = new Blob([text], {type: type});
	a.href = URL.createObjectURL(file);
	a.download = name;
}

$(document).ready(function(){
	download(text ,"transcript.txt", 'text/plain')
});
