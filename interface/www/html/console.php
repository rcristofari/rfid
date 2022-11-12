<!DOCTYPE html>
<html>
<META HTTP-EQUIV="refresh" CONTENT="120">  


<head> 
<title>ANTAVIA MOBILE</title>
<link rel="stylesheet" href="./styles.css"/>

<!-- <script src="https://cdnjs.cloudflare.com/ajax/libs/paho-mqtt/1.0.1/mqttws31.js" type="text/javascript"></script> -->
<script type='text/javascript' src='js/paho-mqtt.js'></script>

<script type = "text/javascript" language = "javascript">

    // Create a client instance
    client = new Paho.MQTT.Client(location.hostname, 9001, "webApp");

    // set callback handlers
    client.onConnectionLost = onConnectionLost;
    client.onMessageArrived = onMessageArrived;

    // connect the client
    client.connect({onSuccess:onConnect});

    // called when the client connects
    function onConnect() {
      // Once a connection has been made, make a subscription and send a message.
      console.log("Connected to MQTT broker");
      client.subscribe("detections/all");
      //message = new Paho.MQTT.Message("Hello");
      //message.destinationName = "detections/all";
      //client.send(message);
    }

    // called when the client loses its connection
    function onConnectionLost(responseObject) {
      if (responseObject.errorCode !== 0) {
        console.log("onConnectionLost:"+responseObject.errorMessage);
      }
    }

    // called when a message arrives
    function onMessageArrived(message) {
      let antenna = "";
      let rfid = "";
      let name = "";
      let detection_time = "";

      console.log("New message: " + message.payloadString);
      const msg = message.payloadString.split(",")

      // rfid tag number
      rfid = msg[4].substr(0, 1) + "~" + msg[4].substr(msg[4].length - 16);

      // name
      if (msg[5].substr(0, 5) == "auto_") {
        name = "auto";
      } else {
        name = msg[5];
      }

      // detection date and time
      const Y = 2000 + parseInt(msg[2].substr(4, 2));
      const m =msg[2].substr(2, 2);
      const d = msg[2].substr(0, 2);
      const H = msg[3].substr(0, 2);
      const M = msg[3].substr(2, 2);
      const S = msg[3].substr(4, 2);
      detection_time = Y + "-" + m + "-" + d + " " + H + ":" + M + ":" + d;

      // antenna name
      antenna = msg[1].substr(0, 18).padEnd(18, ".");

      document.getElementById('rfidbox').insertAdjacentHTML('afterbegin', antenna + "| " + detection_time + " | " + rfid + " | " + name + "<br>");
    }
</script>

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
  <li><a href="index.php">Home</a></li>
  <li><a class="active" href="console.php">Console</a></li>
  <li><a href="control.php">Control</a></li>
  <li><a href="settings.php">Settings</a></li>
  <li><a href="tuning.php">Tuning</a></li>
  <li><a href="help.html">Help</a></li>
  </ul>
</div>

<body>

<h2>Live RFID monitor</h2>
<hr>

<!-- Load the last 10 detections from the sqlite database and pre-fill the console window (prevents blank screen at refresh)-->
<?php
    #echo "Trying...";
    $last = shell_exec('sqlite3 sqlite/detections.db "select date, nmea from detections order by date desc limit 30;"');
    $sentences = explode("\n", $last);
    echo '<div class="rfid", id="rfidbox", style="font-size: 2vw; font-family: monospace;">';
    for($i=0; $i<30; $i++){
      $date_nmea = explode("|", $sentences[$i]);
      $items = explode(",", $date_nmea[1]);
      $rfid = substr($items[4], 0, 1) . '~' . substr($items[4], (strlen($items[4])-16), 16);
      $dtime = $date_nmea[0];
      $name = $items[5];
      $line =  str_pad($items[1], 18, ".") . '| ' .  $dtime . ' | ' . $rfid . ' | ' . $name;
      echo $line;
      echo nl2br("\r\n");
    }
    echo '</div>';
?>

<!-- Use the following if skipping the db loading-->
<!--<div class="rfid", id="rfidbox"></div>-->
<br><br><hr>
<div class="footer">Robin Cristofari / Yoann Depalle / Theo Evrard</div>

</body>
</html>
