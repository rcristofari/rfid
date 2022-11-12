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
    <h1>P137 - POLAROBS
    <br>
    MOBILE SYSTEM</h1>
  </div>
</div>
</header>

<div class="topnav">
  <ul>
  <li><a class="active" href="#home">Home</a></li>
  <li><a href="console.php">Console</a></li>
  <li><a href="control.php">Control</a></li>
  <li><a href="settings.php">Settings</a></li>
  <li><a href="tuning.php">Tuning</a></li>
  <li><a href="help.html">Help</a></li>
  </ul>
</div>

<body>
  
<p>Welcome to the PolarObs Mobile system. This is a prototype, so bugs are quite possible: don't hesitate to document them as well as you can, and to send us reports and suggestions as they come! <br> System version: V1.1 beta (septembre 2022)</p>

<hr>
<h2>System status</h2>
  
    <?php
              $output = shell_exec('systemctl status rfid.service | head -3 | tail -1');
              if(strpos($output, 'dead') !== false){
                $col='#7D1128';
              } else {
                $col ='#4B7F52';
              }
              echo '<div class="code", style="background-color: ' . $col . ';">';
              echo $output;
              echo '</div>';
    ?>

<br><hr>
<h2>Data download</h2>
<p>Select the period you are interested in, and click "submit". This will prepare the data file. When it is ready, you can download it by using the link below.</p> 

<?php
  if(isset($_GET['submit'])) {
    $start = htmlentities($_GET['start_date']);
    $end = htmlentities($_GET['end_date']);
    if($start > $end){
      echo "ERROR: end date cannot be anterior to start date";
    } else {
      $valid = 1;
    }
  }
?>

<?php
  if(isset($valid) && $valid == 1){
    # Clear the data folder and initiate the new file:
    shell_exec("rm -rf data/*");
    shell_exec("echo '#----------DATA SECTION----------' > data/detections.txt");

    # Add the detection data:
    $cmd = "select nmea from detections where date >= '" . $start . " 00:00:00' and date <= '" . $end . " 29:59:59';";
    shell_exec("sqlite3 sqlite/detections.db \"" . $cmd . "\" >> data/detections.txt");
    # Add the log section:
    $pycmd = "python3 python3/getLog.py " . $start . " " . $end;
    shell_exec($pycmd);

    # Rename that file using dates and antenna name:
    $config_file = fopen("/var/www/html/config.yaml", "r") or die ('Cant open file');
    while(!feof($config_file)){
      $line=fgets($config_file);
      if(substr($line, 0, 12)=="antenna_name"){
        list($var, $value) = explode(": ", $line);
      }
    }
    $basename = "data_" . strtolower(trim($value, "\n")) . "_". $start . "_" . $end . ".txt";
    $filename = "data/" . $basename;
    shell_exec("mv data/detections.txt ". $filename);
    echo "<div class='button', style='width: 92%; color: #FFFFFF; text-align: center;'>";
    echo '<a href="download.php?file=' . urlencode($basename) . '" style="font-size: 3.5vw; color: #FFFFFF;">' . $basename . '</a>';
    echo "</div>";
    echo "<br>";

  }

  unset($valid);
?>

<form action="", method="get">
  <label for="from" style='color: #193B63; font-size: 100%;'>start:</label>
  <input type="date" id="start_date" name="start_date" style='color: #193B63; font-size: 100%;'></input>
  <label for="to" style='color: #193B63; font-size: 100%;'>end:</label>
  <input type="date" id="end_date" name="end_date" style='color: #193B63; font-size: 100%;'></input>
  <input type="submit" name="submit" value="send" style='font-size: 100%; background: #193B63; border-color: #193B63; border-radius: 5%; color: #FFFF;'></input>
</form>

<br><br><hr>
<div class="footer">Robin Cristofari / Yoann Depalle / Theo Evrard</div>

</body>
</html>
