<!DOCTYPE html>
<html>
<META HTTP-EQUIV="refresh" CONTENT="120">  


<head> 
<title>ANTAVIA MOBILE</title>
<link rel="stylesheet" href="./styles.css"/> 
</head>


<header>  
<div class="div1">
  <img class="img" src="./resources/IPEV_logo.png"/> 
  <div class="div2">
    <h1>P137 - ANTAVIA
    <br>
    MOBILE SYSTEM</h1>
  </div>
</div>
</header>

<div class="topnav">
  <ul>
  <li><a href="index.php">Home</a></li>
  <li><a href="status.php">Status</a></li>
  <li><a href="settings.php">Settings</a></li>
  <li><a href="#Tuning">Tuning</a></li>
  <li><a href="help.html">Help</a></li>
  </ul>
</div>

<body>
  
<h2>Data archive</h2>
<p>Here, you can download older data files - in order to prevent accidental loss, data can only be deleted manually (ask your local antenna of LOG-LOVES-YOU<sup>TM</sup> or see the help section).</p>
<HR>
    <?php
    $files = scandir('/var/www/html/data/');
    foreach($files as $file){
		if(substr($file,0,4)=="data"){
			echo '<a href="download.php?file=' . urlencode($file) . '", class="datalink">' . $file . '</a><br>';
		}
	}
    ?>


<BR><HR>
<div class="footer">Robin Cristofari / Yoann Depalle / Theo Evrard</div>

</body>
</html>
