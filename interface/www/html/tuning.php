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
  <li><a href="control.php">Control</a></li>
  <li><a href="settings.php">Settings</a></li>
  <li><a class="active" href="#">Tuning</a></li>
  <li><a href="help.html">Help</a></li>
  </ul>
</div>


<body>

<p><em>To find the appropriate jumper setting for the antenna tuning board, enter the impedance value for the antenna (measured in &mu;H with an LCR meter, with the antenna powered off, and already in it's final position). Fine-tune the antenna by adjusting the self with a plastic screwdriver (no metal allowed!). If you cannot find a satisfactory setting, try the proposed (lower or upper) alterative jumper settings.</em></p>

<hr>

<form action="#">
    <div class="textbox">
      <form action="#">
        <div class="colums">
          <div class="item">
            <label for="L_ant" style="float: left;">Impedance (&mu;H): </label>
            <input id="L_ant" type="number" step="0.01" name="L_ant" value="" style="font-size: 100%; float: right;" required/>
          </div>
        </div>
        <p><em></em></p>
    </div>
    
    <br><br>

    <div class="btn-block">
      <button type="submit" href="/" class="button">Calculate</button>
    </div>
    <br>
    <?php

        if(isset($_GET['L_ant']) && !empty($_GET['L_ant'])){
            $C_res = 1406.45 / (($_GET['L_ant']) + 3);
            $C_tunb = $C_res - 2.2;
            if ($C_tunb <= 19){
              $JP_prev = "";
              $JP = "JP2";
              $JP_next = "JP2 | JP11";
            } elseif ($C_tunb > 19 & $C_tunb <= 22.5) {
              $JP_prev = "JP2";
              $JP = "JP2 | JP11";
              $JP_next = "JP2 | JP8";
            } elseif ($C_tunb > 22.5 & $C_tunb <= 28.25) {
              $JP_prev = "JP2 | JP11";
              $JP = "JP2 | JP8";
              $JP_next = "JP2 | JP5";
            } elseif ($C_tunb > 28.25 & $C_tunb <= 35.5) {
              $JP_prev = "JP2, JP8";
              $JP = "JP2 | JP5";
              $JP_next = "JP2 | JP5 | JP11";
            } elseif ($C_tunb > 35.5 & $C_tunb <= 41.75) {
              $JP_prev = "JP2 | JP5";
              $JP = "JP2 | JP5 | JP11";
              $JP_next = "JP2 | JP5 | JP8 | JP11";
            } elseif ($C_tunb > 41.75 & $C_tunb <= 55.75) {
              $JP_prev = "JP2 | JP5 | JP11";
              $JP = "JP2 | JP5 | JP8 | JP11";
              $JP_next = "JP3 | JP4";
            } elseif ($C_tunb > 55.75 & $C_tunb <= 70.25) {
              $JP_prev = "JP2 | JP5 | JP8 | JP11";
              $JP = "JP3 | JP4";
              $JP_next = "JP2 | JP4 | JP7 | JP10";
            } elseif ($C_tunb > 70.25 & $C_tunb <= 78.50) {
              $JP_prev = "JP3 | JP4";
              $JP = "JP2 | JP4 | JP7 | JP10";
              $JP_next = "JP1 | JP3 | JP5";
            } elseif ($C_tunb > 78.50 & $C_tunb <= 87.50) {
              $JP_prev = "JP2 | JP4 | JP7 | JP10";
              $JP = "JP1 | JP3 | JP5";
              $JP_next = "JP1 | JP3 | JP5 | JP10";
            } elseif ($C_tunb > 87.50 & $C_tunb <= 108.25) {
              $JP_prev = "JP1 | JP3 | JP5";
              $JP = "JP1 | JP3 | JP5 | JP10";
              $JP_next = "JP1 | JP3 | JP4 | JP7 | JP10";
            } else {
              $JP_prev = "JP1 | JP3 | JP5 | JP10";
              $JP = "JP1 | JP3 | JP4 | JP7 | JP10";
              $JP_next = "";
            }
          echo "<p style='font-size: 150%;'>Lower setting: " . $JP_prev . "</em></p>";
          echo "<p style='font-size: 150%;'><b>Main setting: " . $JP . "</b></p>";
          echo "<p style='font-size: 150%;'>Upper setting: " . $JP_next . "</p>";
        }
    ?>

</form>


<BR><HR>
<div class="footer">Robin Cristofari / Yoann Depalle / Theo Evrard</div>

  </body>
</html>
