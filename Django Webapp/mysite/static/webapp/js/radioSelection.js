$(document).ready(function(){
	document.getElementById('cardText').innerHTML = compData["one"];
	$("#infoType").change(function () {
		if ($("#option1").is(":checked")) {
			document.getElementById('cardText').innerHTML = compData["one"];
		}
		else if ($("#option2").is(":checked")){
			document.getElementById('cardText').innerHTML = compData["two"];
		}
		else if ($("#option3").is(":checked")){
			document.getElementById('cardText').innerHTML = compData["lang"];
		}
	});
});