<?php

/*
 * generate a file with an uniqid name
 */
function generateUniqidTxt($filePath, $fileContent) 
{
	file_put_contents($filePath, $fileContent);
}

/*
 * delete all images which are more than 100 seconds
 */
function deleteOldImages()
{
	// the path of images 
	$dirPath = "./python/images";
	$handle = opendir($dirPath);
	
	// get the current time
	$currentTime = time();
	
	$mTime = 0;

	// read all files
	while (false !== ($entry = readdir($handle)))
	{	
		
		// save the modified time for this file
		$mTime = filemtime($dirPath."/".$entry);
		
		// delete images
		if (($currentTime - $mTime) > 20 && !is_dir($dirPath."/".$entry))
		{
			unlink($dirPath."/".$entry);
		}
	}
}

/*
 * count the visitors
 */
function incrementCounter($filename)
{
	$file = fopen($filename, "r");
	$visits = fgets($file);
	fclose($file);
	//echo "Visits: $visits";
	$file = fopen($filename, "w");
	fputs($file, $visits + 1);
	fclose($file);
}

/*
 * Open a file and save the name and organization to the file
 */
function nameAndOrganization($fileName, $visitorName, $organization)
{
	date_default_timezone_set('America/Denver');
	// get the current time of the server
	$currentTime = date("l jS \of F Y h:i:s A");
	
	$file = fopen($fileName, "a");
	$append = $visitorName . ", " . $organization . ", ". $currentTime . "\n";
	fputs($file, $append);
	fclose($file);
}
?>
