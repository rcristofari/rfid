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
  <li><a href="console.php">Console</a></li>
  <li><a class="active" href="#Control">Control</a></li>
  <li><a href="settings.php">Settings</a></li>
  <li><a href="tuning.php">Tuning</a></li>
  <li><a href="help.html">Help</a></li>
  </ul>
</div>

<body>

<h2>RFID control</h2>
  <p><em>Click here to start, restart or stop the RFID service (not the whole RFID unit, just the software itself). This may be useful is the system is stuck. </em></p>
  <div class="form_button_div">
    <form action="status.php" method="post">
      <input type="submit" name="Start" value="Start" class="form_button"/>
    </form>
    <?php
        if($_SERVER['REQUEST_METHOD'] == 'POST' and $_POST['Start']) {
           shell_exec('sudo /bin/systemctl start rfid.service');
            echo '<script type="text/javascript">';
            echo 'alert("RFID started")';
            echo '</script>';
        }
    ?>
  </div>
  <div class="form_button_div">
    <form action="status.php" method="post">
      <input type="submit" name="Restart" value="Restart" class="form_button"/>
    </form>
    <?php
        if($_SERVER['REQUEST_METHOD'] == 'POST' and $_POST['Restart']) {
           shell_exec('sudo /bin/systemctl restart rfid.service');
            echo '<script type="text/javascript">';
            echo 'alert("RFID restarted")';
            echo '</script>';
        }
    ?>
  </div>

  <div class="form_button_div">
    <form action="status.php" method="post">
      <input type="submit" name="Stop" value="Stop" class="form_button"/>
    </form>
    <?php
        if($_SERVER['REQUEST_METHOD'] == 'POST' and $_POST['Stop']) {
           shell_exec('sudo /bin/systemctl stop rfid.service');
            echo '<script type="text/javascript">';
            echo 'alert("RFID stopped ")';
            echo '</script>';
        }
    ?>
  </div>

<br><br><br><hr>
<h2>System control</h2>    
<p><em>Click here to stop or restart the antenna totally - this will take a few minutes and <b>the WiFi hotspot will go down</b>, this is normal.</em></p>
  <div class="form_button_div">
    <form action="control.php" method="post">
      <input type="submit" name="halt" value="Shutdown" class="form_button_2"/>
    </form>
    <?php
        if($_SERVER['REQUEST_METHOD'] == 'POST' and $_POST['halt']) {
           shell_exec('sudo /usr/sbin/halt -h');
        }
    ?>
  </div>

  <div class="form_button_div">    
    <form action="control.php" method="post">
      <input type="submit" name="reboot" value="Reboot" class="form_button_2"/>
    </form>
    <?php
        if($_SERVER['REQUEST_METHOD'] == 'POST' and $_POST['reboot']) {
           shell_exec('sudo /usr/sbin/reboot -f');
        }
    ?>
  </div>

<br><br><br><hr>
<h2>Battery</h2>

<canvas id="batteryGraph" style="width:100%;"></canvas>

<script type='text/javascript' src='js/chart.js'></script>
<script type='text/javascript' src='js/luxon.js'></script>
<script type='text/javascript' src='js/luxon-adapter.js'></script>
<script type='text/javascript' src='data/battery.js'></script>
<?php shell_exec("python3 python3/getVoltages.py"); ?>

<script type = "text/javascript" language = "javascript">

  // Parse the JSON file
  var labels = jsonfile.voltage.map(function(e) {
    return e.dtime;
  });

  var data = jsonfile.voltage.map(function(e) {
    return e.V;
  });

  // Graph:
  var ctx = document.getElementById('batteryGraph').getContext('2d');

  var config = {
     type: 'line',
     data: {
       labels: labels,
       datasets: [{
         data: data,
         lineTension: 0.1,
         //backgroundColor: "#3B80CE",
         borderColor: "#193B63",
         fill: true
       }]
     },
     options: {
     plugins: {legend: {display: false,},},
     scales: {
       x: {
           type: 'time',
           time: {units: 'hours'}
       }
     }
    },
  };

  var chart = new Chart(ctx, config);
</script>

<br><hr>
<h2>Recent activity</h2>
  <div class="code">
  <?php
      $last_7_days = shell_exec('sqlite3 sqlite/detections.db "select count(date) from detections where julianday(\'now\') - julianday(date) <= 7;"');
      $last_24_hours = shell_exec('sqlite3 sqlite/detections.db "select count(date) from detections where julianday(\'now\') - julianday(date) <= 1;"');
      echo "There have been " . $last_7_days . " detections during the past 7 days, including " . $last_24_hours . " during the last 24 hours.";
  ?>
  </div>

<br><hr>
<h2>GPS status</h2>
  <div class="code">
    <?php
              $gpstatus = substr(shell_exec('cat /var/www/antavia_mobile.txt | grep GP | grep -v "valid" | tail -1 | cut -c 2-6'), 0, 5);
              $datetime = date('Y-m-d H:i:s a', time());
              if($gpstatus == "GPRMC"){
                $output = "Time is set by a valid GPS fix. Current system time is UTC ";
              } else {
                $output = "There was no GPS time fix since the last system start. Current system time is UTC ";
              }
              echo $output;
              echo $datetime;
    ?>
  </div>


<br><hr>
<h2>Log</h2>
  <p><em>These are the last 10 lines of the log. You can access the entire log through Home>Data dowwnload.</em></p>
  <div class="code", style="text-align: left; font-size: 60%;">
    <?php
        $output = wordwrap(nl2br(shell_exec('tail -10 /home/pi/antavia_mobile/log/antavia.log')), 45, "\n", True);
        echo $output;
    ?>
  </div>
  
  
<br><hr>
<div class="footer">Robin Cristofari / Yoann Depalle / Theo Evrard</div>

</body>
</html>
