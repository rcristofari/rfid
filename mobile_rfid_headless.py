from rfid_core import *
import sys, serial, threading, queue, logging, time
import paho.mqtt.client as mqtt


version = "1.1"

log_file, conf_file, penguins_dbfile, detections_dbfile, detections_txtfile, fontfile = read_paths("/home/pi/antavia_mobile/conf/paths.conf", system="mobile")

if __name__ == '__main__':

    #------------------------------------------------------------------------------------------------------------------#
    # Initialize the logger file
    logging.basicConfig(filename=log_file, filemode='a', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    logger = logging.getLogger()
    # Redirect the logger to stdout:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    hformatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    handler.setFormatter(hformatter)
    logger.addHandler(handler)

    logging.info(f"-----------------------------------------------------")
    logging.info(f"POLAROBS MOBILE RFID VERSION {version} - STARTING ACQUISITION")

    #------------------------------------------------------------------------------------------------------------------#
    # Loading the settings from the PHP interface and initializing variables
    antenna_name, base_freq, n_antennas, use_lcd = read_settings(conf_file)
    logging.info(f"Antenna name {antenna_name}, detecting on {n_antennas} antennas at {base_freq} Hz.")
    #logging.info(f"Sleeping penguin mode is switched {'ON' if sleeping_penguin else 'OFF'}")

    #------------------------------------------------------------------------------------------------------------------#
    # Initialize the LCD display
    if use_lcd:
        logging.info("Initializing the LCD display")
        display = Display(fontfile)
        display.text(f"POLAROBS MOBILE\nRFID SYSTEM\nRobin CRISTOFARI\nv{version}", center=True)
#        time.sleep(2)
    else:
        display = None
        logging.info("LCD display is not in use")

    # ------------------------------------------------------------------------------------------------------------------#
    # Set up some operating parameters
    # Multiply frequency by the number of antennas so that each antenna fires at the desired frequency:
    base_freq = base_freq * n_antennas
    pulse = 1000 / base_freq  # in milliseconds

    #------------------------------------------------------------------------------------------------------------------#
    # Scan for serial devices
    devices = scan_devices()

    # If no TIRIS is found, execution will halt.
    if devices["TIRIS"] is None:
        logging.error("TIRIS reader not found. Aborting.")
        if use_lcd:
            display.text("ERROR\n*TIRIS NOT FOUND*", center=True) ### MAYBE TURN OFF THE RPi entirely ?

    else:
        # Give warnings if GPS and Iridium are not detected
        if devices["GPS"] is None:
            logging.warning("GPS receiver not found. Interpret time data with caution.")
            gps = None
            if use_lcd:
                display.text("WARNING\n*GPS NOT FOUND*", center=True)
    #            time.sleep(3)
        else:
            gps = GPSDevice(f"/dev/ttyUSB{devices['GPS']}")

        if devices["IRIDIUM"] is None:
            logging.warning("Iridium modem not found. Data will be stored locally only.")
            if use_lcd:
                display.text("WARNING\n*IRIDIUM*\n*NOT FOUND*", center=True)
                #time.sleep(3)

        n_antennas = 1
        #------------------------------------------------------------------------------------------------------------------#
        # Get a GPS fix and set time (blocking ?) Or run this in parallel, monitoring time drift ? Or just skip it entirely
        # and see if Navman can by itself manage system time.

        #------------------------------------------------------------------------------------------------------------------#
        # Initialize the data queues
        detection_queue = queue.SimpleQueue()
        nmea_queue = queue.SimpleQueue()

        #------------------------------------------------------------------------------------------------------------------#
        # Initialize the TIRIS connexion:
        if use_lcd:
            display.text("STARTING\nRFID\nACQUISITION", center=True)
        #    time.sleep(1)

        logging.info("Initializing the serial TIRIS reader thread")
        tiris = TirisReader(f"/dev/ttyUSB{devices['TIRIS']}", baudrate=9600, timeout=1.0, n_antennas=n_antennas, muxMSB=26, muxLSB=19, mode="SLAVE")
        tiris_process = threading.Thread(target=tiris.monitor, args=(detection_queue, pulse, display,))
        tiris_process.start()
        
        #------------------------------------------------------------------------------------------------------------------#
        # Initialize the SQLite3 connections:
        logging.info(f"Initializing the SQLite3 penguin database at {penguins_dbfile}")
        logging.info(f"Initializing the SQLite3 detection database at {detections_dbfile}")
        dbcon = Sqlite3Connect(penguins_dbfile, detections_dbfile)

        #------------------------------------------------------------------------------------------------------------------#
        # Initialize the detection processing thread:
        logging.info("Initializing the detection processing thread")
        sqlite_process = threading.Thread(target=handle_detections_mobile, args=(dbcon, detection_queue, nmea_queue, detections_txtfile, antenna_name,))
        sqlite_process.start()
        
        #------------------------------------------------------------------------------------------------------------------#
        # Start the MQTT client
        logging.info("Starting the MQTT broker connexion")
        client = mqtt.Client("nmea_stream")
        ##client.on_connect = mqtt_on_connect # this does not work yet, check it out
        ##client.mqtt_on_publish = mqtt_on_publish
        client.connect("localhost", 1883)
        client.loop_start()
        #client._connect_timeout = 0 # this probably needs to be added in the fixed version too !

        logging.info("Starting the detection broadcasting thread")
        broadcast_rfid = threading.Thread(target=broadcast_detections, args=(client, nmea_queue))
        broadcast_rfid.start()

        #------------------------------------------------------------------------------------------------------------------#
        # Initialize clock-like logging processes, periodic tasks and pushbutton monitoring
        hourly_logger = threading.Thread(target=hourly_logging, args=(gps,)) # The detections in hour doesn't work like that - pass it along another way if needed
        hourly_logger.start()
