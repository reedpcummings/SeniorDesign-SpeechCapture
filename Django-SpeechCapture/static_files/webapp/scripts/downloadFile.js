function download(fileName, contentName) {
    var a = document.createElement("a");
    document.body.appendChild(a);
    a.style = "display: none";
    var content = document.getElementById(contentName).textContent.replace(/\s{4,}/g, "\n").trim();
    var blob = new Blob([content], {type: 'text/plain'});
    url = window.URL.createObjectURL(blob);
    a.href = url;
    a.download = fileName;
    a.click();
    window.URL.revokeObjectURL(url);
}

$(document).ready(function(){
    $(document.getElementById('saveButtonSummary')).click(function() {
	    download("summary.txt", 'summaryCont')
    });

    $(document.getElementById('saveButtonQuestions')).click(function() {
	    download("q&a.txt", 'questionCont')
    });

    $(document.getElementById('saveButtonUseCase')).click(function() {
	    download("usecases.txt", 'useCaseCont')
    });
});
