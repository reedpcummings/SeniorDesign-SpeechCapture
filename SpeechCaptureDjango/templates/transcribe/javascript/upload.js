function upload(blob) {
    //AJAX upload BLOB
    var form = new FormData();
    form.append('audio_test', blob);

    $.ajax({
        url: 'http://localhost:8000/transcribe/record/',
        type: 'POST',
        data: form,
        processData: false,
        contentType: false,
        success: function (data) {
            console.log('response' + JSON.stringify(data));
        },
        error: function () {
            console.log("you dun messed up")
        }
    });
}