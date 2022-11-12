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

<script type="text/JavaScript">
  function valid(f) {
    !(/^[A-z&0-9]*$/i).test(f.value)?f.value = f.value.replace(/[^A-z&0-9]/ig,''):null;
  } 
</script>

</header>

<div class="topnav">
  <ul>
  <li><a href="index.php">Home</a></li>
  <li><a href="console.php">Console</a></li>
  <li><a href="control.php">Control</a></li>
  <li><a class="active" href="#">Settings</a></li>
  <li><a href="tuning.php">Tuning</a></li>
  <li><a href="help.html">Help</a></li>
  </ul>
</div>


<body>

    <?php
          # Add a check whether file exists, if not create one
          $config_file = fopen("/var/www/html/config.yaml", "r") or die ("Can't open file");
          while(!feof($config_file)){
            list($var, $value) = explode(": ", fgets($config_file));
            if($var=="antenna_name"){
              $antenna_name = trim($value, "\n");
            } elseif($var=="base_freq"){
              $base_freq = trim($value, "\n");
            } elseif($var=="n_antennas"){
              $n_antennas = trim($value, "\n");
            } elseif($var=="sleeping_penguin"){
              $sleeping_penguin = trim($value, "\n");
            } elseif($var=="site"){
              $site = trim($value, "\n");
            }
          }
    ?>


<p><em>Here, you can set the main operating parameters for the RFID unit:</em></p>

<hr>

    <div class="textbox">
      <form action="#">
        <div class="colums">
          <div class="item">
            <label for="antenna_name"> Antenna Name <span>*</span></label>
            <?php
              echo "<input id='antenna_name' type='text' name='antenna_name' value='" . $antenna_name . "' onkeyup='valid(this)' onblur='valid(this)' style='font-size: 100%; float: right;' required/>";
            ?>
          </div>
        </div>
        <p><em>This name will identify the antenna in the log files.</em></p>
    </div>

<hr>

        <div class="question">
          <label>Number of antennas</label>
          <p><em>How many physical antennas are connected to the detection unit? (usually one for mobile systems, two for semi-fixed systems like Antavia 0 - up to 4 may be supported).</em></p>

          <div class="question-answer">
            <?php
              for($i=1; $i<=4; $i++){
                echo "<div class='radio'>";
                if(strval($i) == $n_antennas){
                  echo "<input type='radio' value='" . strval($i) . "' id='radio_" . strval($i) . "' name='n_antennas' checked='checked'/>";
                } else {
                  echo "<input type='radio' value='" . strval($i) . "' id='radio_" . strval($i) . "' name='n_antennas' />";
                }
                echo "<label for='radio_" . strval($i) . "' class='radio'><span>" . strval($i) . "</span></label>";
                echo "</div>";
              }
            ?>

          </div>
        </div>

<hr>

        <div class="question">
          <label>Detection frequency</label>
          <p><em>Number of detection pulses per second, per antenna. Higher values may lead to more detections if many marked penguins are in the area (e.g. Antavia 0) but will use more battery.</em></p>
          <div class="question-answer">
            <?php
              for($i=1; $i<4; $i++){
                $freq = pow(2, $i);
                echo "<div class='radio'>";
                if(strval($freq) == $base_freq){
                  echo "<input type='radio' value='" . strval($freq) . "' id='radio_" . strval($i+4) . "' name='base_freq' checked='checked'/>";
                } else {
                  echo "<input type='radio' value='" . strval($freq) . "' id='radio_" . strval($i+4) . "' name='base_freq' />";
                }
                echo "<label for='radio_" . strval($i+4) . "' class='radio'><span>" . strval($freq) . " Hz</span></label>";
                echo "</div>";
              }
            ?>
          </div>
        </div>

<hr>


<!--
        <div class="question">
          <label>Sleeping penguin mode </label>
          <p><em>If a penguin is detected for over 2 minutes on the antenna, the antenna will stop transmitting, and send one pulse every 5 minutes to test if the penguin is still there.</em></p>
          <div class="question-answer">
            <div class="radio">
              <?php
                if($sleeping_penguin=="True"){
                  echo "<input type='radio' value='True' id='radio_9' name='sleeping_penguin' checked='checked'/>";
                } else {
                  echo "<input type='radio' value='True' id='radio_9' name='sleeping_penguin'/>";
                }
              ?>
              <label for="radio_9" class="radio"><span>ON</span></label>
            </div>
            <div class="radio">
              <?php
                if($sleeping_penguin=="False"){
                  echo "<input type='radio' value='False' id='radio_10' name='sleeping_penguin' checked='checked'/>";
                } else {
                  echo "<input type='radio' value='True' id='radio_10' name='sleeping_penguin'/>";
                }
              ?>
              <label for="radio_10" class="radio"><span>OFF</span></label>
            </div>
          </div>
        </div>
  
<hr>
-->
        <div class="btn-block">
          <p><em>When you click "save", the RFID will be restarted to take the new settings into account.</em></p>
          <button type="submit" href="/" class="button">Save & Restart RFID</button>
        </div>
      </form>

    <?php

        if(isset($_GET['antenna_name']) && !empty($_GET['antenna_name'])){
            $config_file = fopen("/home/pi/AntaviaMobile/tmp_files/config.yaml", "w") or die ('Cant open file');
            fwrite($config_file, 'antenna_name: ' . $_REQUEST['antenna_name'] . "\n");
            fwrite($config_file, 'base_freq: ' . $_REQUEST['base_freq'] . "\n");
            fwrite($config_file, 'n_antennas: ' . $_REQUEST['n_antennas'] . "\n");
            fwrite($config_file, 'sleeping_penguin: ' . $_REQUEST['sleeping_penguin'] . "\n");
            fclose($config_file);

            echo '<script type="text/javascript">';
            echo 'alert("Settings changed")';
            echo '</script>';
            
            shell_exec('sudo /bin/systemctl restart rfid.service');
        }

    ?>

<BR><HR>
<div class="footer">Robin Cristofari / Yoann Depalle / Theo Evrard</div>

  </body>
</html>
