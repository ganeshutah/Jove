$(function(){

	// reset the index
	index = 0;
	
	// previous button handler
	$("#previous").click(function(){previousFormula();});
	
	// next button handler
	$("#next").click(function(){nextFormula();});
	
	// buildBDD button handler
	$("#buildBDD").click(function(){buildBDD();});
	
	// buildMinimumBDD button handler
	$("#buildMinimumBDD").click(function(){buildMinimumBDD();});

	// call load page
	loadPage();
});

// all files in the server side
var fileName = ["example1", "example2", "example3",
		"example4", "example5", "example6"];

// file index
var index = 0;

/*
 * When the page loads, it will show the first example on the screen
 */
function loadPage() {
	// save the file name
	var name = fileName[index];

	// ajax call. call loadpage.php to read file content
	$.get("loadPage.php", {fileName: name},loadPageCallback);
}

/*
 * the callback function of load page. It will show paste the content on
 *  the screen
 */ 
function loadPageCallback(result) {
	$('.formulaArea').val(result);
}

/*
 * show the previous formula and copy its content
 * from the file and paste the content on the
 * textarea
 */
function previousFormula() {
	
	// prevent array out of bound
	if (index >= 1) {
		// decrement index
		index--;
		
		// save the file name
		var name = fileName[index];
		
		$.get("previousFormula.php", {fileName: name},previousFormulaCallback);
	}
	else {
		alert("No more examples!");
	}
}

/*
 * the callback function of previous button. 
 * It will show paste the content on the screen
 */ 
function previousFormulaCallback(result) {
	$('.formulaArea').val(result);
}

/*
 * show the next formula and copy its content
 * from the file and paste the content on the 
 * textarea
 */
function nextFormula() {
	
	// prevent array out of bound
	if (index < fileName.length-1) {
		
		// increment index
		index++;
		
		// save the file name
		var name = fileName[index];
		
		$.get("nextFormula.php", {fileName: name},nextFormulaCallback);
	}
	else {
		alert("No more examples!");
	}
}

/*
 * the callback function of next button. 
 * It will show paste the content on the screen
 */ 
function nextFormulaCallback(result) {
	$('.formulaArea').val(result);
}

/*
 * call a python script and generate a graph
 */
function buildBDD() {
	
	// get the content
	var formula = $(".formulaArea").val();
	
	// if the length is less than 1000 characters, pop up an window to tell the user
	if (formula.length <= 2000) {
		// change the text to building
		$('#buildBDD').text("Building...");
		
		// save the formula in the formula area
		var fileContent = $('.formulaArea').val();
		$.get("buildBDD.php",{file: fileContent}, buildBDDCallback);
	}
	else {
		alert("Formulas for the web interface must be under 2000 characters");
	}
}


function buildBDDCallback(result) {
	// change the text back
	$('#buildBDD').text("Build BDD");
	// get flag
	var flag = result[0];

	// a time out message will be show on the output 
	if (flag == "timeOut") {
		var output = result[1];

		// paste to output area
		$('.outputArea').val(output);
	}
	// if flag is false, an error.txt was generated
	else if (!flag) {
		// save the content
		var fileContent = result[1];
		
		// clear the image
		$('.imageArea').attr('src', "#");
		
		// paste to output area
		$('.outputArea').val(fileContent);
	}
	// if flag is true, an output.txt and an image were generated
	else {
		// save image url and file content
		var imageUrl = result[1];
		var fileContent = result[2];
		
		// paste the image and output
		$('.imageArea').attr('src', imageUrl);
		$('.outputArea').val(fileContent);
	}	
}

/*
 * call a python script and generate a graph
 */
function buildMinimumBDD() {
	
	// get the content
	var formula = $(".formulaArea").val();
	
	// if the length is less than 1000 characters, pop up an window to tell the user
	if (formula.length <= 2000) {
		// change the text to building
		$('#buildMinimumBDD').text("Building...");
		
		// save the formula in the formula area
		var fileContent = $('.formulaArea').val();
		
		$.get("buildMinimumBDD.php",{file: fileContent}, buildMinimumBDDCallback);
	}
	else {
		alert("Formulas for the web interface must be under 2000 characters");
	}
}

function buildMinimumBDDCallback(result) {
	
	// change the text to building
	$('#buildMinimumBDD').text("Build minimum BDD");
	
	// get flag
	var flag = result[0];

	// a time out message will be show on the output 
	if (flag == "timeOut") {
		var output = result[1];

		// paste to output area
		$('.outputArea').val(output);
	}
	// if flag is false, an error.txt was generated
	else if (!flag) {
		// save the content
		var fileContent = result[1];
		
		// clear the image
		$('.imageArea').attr('src', "#");
		
		// paste to output area
		$('.outputArea').val(fileContent);
	}
	// if flag is true, an output.txt and an image were generated
	else {
		// save image url and file content
		var imageUrl = result[1];
		var fileContent = result[2];
		
		// paste the image and output
		$('.imageArea').attr('src', imageUrl);
		$('.outputArea').val(fileContent);
	}	
}






