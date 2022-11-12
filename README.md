## RFID
***
Software tools to operate RFID devices, developed for the King penguin monitoring system in Baie du Marin, Crozet Archipelago.
These tools are designed to be installed on a Linux server (Debian-based incl. RaspiOS or Red Hat-based including Fedora).

They run in headless mode, collecting data from an arbitrary number of TIRIS antennas connected on individual serial ports (possibly virtual serial ports over ethernet), parsing the data and storing it into a MySQL database. For building the database, see https://github.com/rcristofari/antavia_db_v2.

Note that these tools are designed to run either on a self-timed system (where RFID acquisition is triggered electronically, through independent quartz timing - the **fixed** mode) or clocked by the system itself (the **mobile** mode). In both cases, system setup will require a bit of configuration before running correctly.
***
#### Installation
###### For a Fixed system
Clone this repository into your target directory, e.g. root home. Note that this will run as root. **You must have MySQL 8.0 and the Mosquitto MQTT broker (there may be a bit of configuration to do there - in this system we do not use a password for the MQTT broker). 

Edit the configuration files in `conf`. The `paths.conf` lists the paths to the configuration files in use (allowing use to switch config easily). **The paths.conf file should be referenced correctly in `fixed_rfid_headless.py`**

The `mysql.conf` file is self-explanatory. The `serial.conf` file lists, for each TIRIS reader (colon-separated): the antenna number, the serial port path, the baudrate, the serial connexion timeout, the antenna name, and the antenna side (land or sea, "Terre" or "Mer").
> **You can comment out a line to disable the corresponding reader if needed.**

You will then need to edit the `rfid.service` file to point explicitly to the `rfid_service.sh` file (full path on your system), and to edit the `rfid_service.sh` file to reflect the full path to `fixed_rfid_headless.py`. You can then copy the `rfid.service`file to `/lib/systemd/system` (or equivalent on your system), then run

`sudo systemctl enable rfid.service`

The system can then be started / restarted using `systemctl` commands, and will start automatically when the acquisition machine start. It will also restart in case of crash.

**Log files** are created on the machine (path defined in `paths.conf`). They should not be too verbose but it may be a good idea to check them regularly and to include them in the `logrotate` schedule.

###### For a mobile system
A mobile system will require more system-wide configuration - the best is to use a complete ISO disk image (request from r.cristofari@gmail.com, too large for github!). In general, the RFID acquisition is installed as above, but using the `mobile_rfid_headless.py` launcher.

As the system is run autonomously on a Raspberry Pi computer, detection data is stored in a local sqlite3 database. A second sqlite3 database is used to store basic information about all deployed RFID tags.

The `interface` folder include a full php/javascript interface, including a MQTT client. It should be placed in `/var/www`, with the apache server installed.

The system as currently designed uses the WittyPi4 board for power management (https://www.uugear.com/product/witty-pi-4/). The corresponding tools are installed in `/home/pi/WittyPi4`.

**Full system electornics / assembly plans coming soon.**

***
*This module is part of the 2022-2023 update of the Antavia system in Crozet, featuring a new suite of tools for acquisition of RFID penguin monitoring data. 
For the **SPHENOSCOPE** front end visualisation software, please see https://github.com/rcristofari/sphenoscope. For migration tools to initialize the database from the legacy version, see https://github.com/rcristofari/antavia_db_v2. Finally, the database can be explored and managed using the dedicated **SPHENOTRON** software, available here: https://github.com/g-bardon/Sphenotron_Python (work in progress).*
