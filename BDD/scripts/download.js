$(function(){
	
	var flag = false;
	
	var nameFlag = false;
	var organFlag = false;
	
	// previous button handler
	$("#submit").click(function(){saveNameAndOrganization()});
	
	// disabled the submit button
	$("#submit").attr('disabled', 'disabled');
	
	// when a key is up, remove disable attr
	$("#username").keyup(function(){
		nameFlag = true;		
		if (nameFlag && organFlag) {
			$("#submit").removeAttr("disabled");
		}
		
		if ($("#username").val() == "" || $("#organization").val() == "") {
			// disabled the submit button
			$("#submit").attr('disabled', 'disabled');
		}
	});
	
	// when a key is up, remove disable attr
	$("#organization").keyup(function(){
		organFlag = true;	
		if (nameFlag && organFlag) {
			$("#submit").removeAttr("disabled");
		}
		
		if ($("#username").val() == "" || $("#organization").val() == "") {
			// disabled the submit button
			$("#submit").attr('disabled', 'disabled');
		}
	});
});

// An ajax call to save name and orgination to a file
function saveNameAndOrganization() {
	var name = $("#username").val();
	var organization = $("#organization").val();

	if (name.length <= 50 && organization.length <= 100) {
		$.get("SaveNameAndOrganization.php", {name:name, organization:organization}, saveNameAndOrganizationCallback);
	}
	else {
		if (name.length > 50 && organization.length <= 100) {
			alert("The maximum length for name is 50 characters");
		}
		else if (name.length <= 50 && organization.length > 100) {
			alert("The maximum length for organization is 100 characters");
		}
		else {
			alert("The maximum length for name is 50 characters and the maximum length for organization is 100 characters");
		}
	}
}

function saveNameAndOrganizationCallback() {
	// reset text box and button
	$("#username").val("");
	$("#organization").val("");
	
	// disabled the submit button
	$("#submit").attr('disabled', 'disabled');
	
	alert("Thank you!");
}