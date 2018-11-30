function upload(blob) {
    //AJAX upload BLOB
    var form = new FormData();
    form.append('audio_test', blob);

    $.ajax({
        url: 'http://localhost:8000/upload/',
        type: 'POST',
        data: form,
        processData: false,
        contentType: false,
        success: function (data) {
            console.log('response' + " " + (data));
            document.getElementById("transcribeLink").href="http://localhost:8000/transcript/" + data; //$('#transcribeLink').attr('href',"http://localhost:8000/transcript/" + data);
        },
        error: function () {
            console.log("you dun messed up")
         }
    });
}