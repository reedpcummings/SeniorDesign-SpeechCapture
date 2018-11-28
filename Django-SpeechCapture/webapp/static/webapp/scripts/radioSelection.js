$(document).ready(function(){
    $(document.getElementById('summaryCont')).show();
    $(document.getElementById('questionCont')).hide();
    $(document.getElementById('useCaseCont')).hide();
    $(document.getElementById('summary')).click(function() {
        $(document.getElementById('summaryCont')).show();
        $(document.getElementById('questionCont')).hide();
        $(document.getElementById('useCaseCont')).hide();
    });

    $(document.getElementById('questions')).click(function() {
	    $(document.getElementById('questionCont')).show();
	    $(document.getElementById('summaryCont')).hide();
	    $(document.getElementById('useCaseCont')).hide();
    });

    $(document.getElementById('useCases')).click(function() {
	    $(document.getElementById('useCaseCont')).show();
	    $(document.getElementById('summaryCont')).hide();
        $(document.getElementById('questionCont')).hide();
    });
});