from rfid_core.core import *
from rfid_core.tirisIO import *
from rfid_core.dbIO import *
from rfid_core.mqttIO import *
from rfid_core.utilities import *
import serial
import threading
import queue
import logging
import paho.mqtt.client as mqtt

version = "0.1"
log_file, serial_conf_file, mysql_conf_file = read_paths("/home/robin/rfid/conf/paths.conf", system="fixed")

# Set to True to use the MIBE database schema
legacy_mode = False


if __name__ == '__main__':

    #------------------------------------------------------------------------------------------------------------------#
    # Initialize the logger file
    logging.basicConfig(filename=log_file, filemode='a', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    logging.info(f"-----------------------------------------------------")
    logging.info(f"ANTAVIA RFID VERSION {version} - STARTING ACQUISITION")

    #------------------------------------------------------------------------------------------------------------------#
    # Initialize the data queues
    db_queue = queue.SimpleQueue()
    stream_queue = queue.SimpleQueue()

    #------------------------------------------------------------------------------------------------------------------#
    # Read serial configuration file:
    nReaders, port_dict, port_paths, passage_names, locations, baudrates, timeouts = read_serial_conf(serial_conf_file)
    # Read mySQL configuration file:
    host, port, usr, pwd, dbname = read_mysql_conf(mysql_conf_file)

    #------------------------------------------------------------------------------------------------------------------#
    # Initialize the TIRIS connexions:
    logging.info(f"Initializing {nReaders} serial TIRIS reader threads")
    threads = list()

    foundAntennas = 0
    validAntennas = []
    for reader_id in range(nReaders):
        logging.info(f"Starting thread {reader_id} on {port_paths[reader_id]} for {passage_names[reader_id]}")
        this_reader = None
        try:
            this_reader = TirisReader(port_paths[reader_id], baudrate=baudrates[reader_id], timeout=timeouts[reader_id], mode="SYNCHRO")
        except serial.serialutil.SerialException:
            logging.error(f"Serial device {port_paths[reader_id]} could not be found, check {serial_conf_file} file.")
        if this_reader:
            reader = threading.Thread(target=this_reader.listen, args=(db_queue, stream_queue, 10))
            threads.append(reader)
            reader.start()
            foundAntennas += 1
            validAntennas.append(reader_id)

    # Remove the invalid antennas from the lists:
    port_paths = [x for i, x in enumerate(port_paths) if i in validAntennas]
    passageNames = [x for i, x in enumerate(passage_names) if i in validAntennas]
    baudrates = [x for i, x in enumerate(baudrates) if i in validAntennas]
    timeouts = [x for i, x in enumerate(timeouts) if i in validAntennas]
    port_dict = dict(zip([x for i, x in enumerate(port_dict) if i in validAntennas], [port_dict[x] for i, x in enumerate(port_dict) if i in validAntennas]))
    nReaders = foundAntennas
    logging.info(f"Active detection running on {foundAntennas} antennas.")

    #------------------------------------------------------------------------------------------------------------------#
    # Connect to MySQL for the main process
    if legacy_mode:
        logging.info("Initializing the main mySQL connexion in legacy (MIBE) mode")
        db = MysqlConnect_LegacyDB(host=host, port=port, usr=usr, pwd=pwd, db=dbname)
    else:
        logging.info("Initializing the main mySQL connexion")
        db = MysqlConnect(host=host, port=port, usr=usr, pwd=pwd, db=dbname)
    db.connect()

    # Initialize the mySQL connexion process
    logging.info("Starting the mySQL processing thread")
    process = threading.Thread(target=handle_detections_fixed, args=(db, db_queue, port_dict, legacy_mode))
    threads.append(process)
    process.start()

    #------------------------------------------------------------------------------------------------------------------#
    # Start a second mySQL connexion for getting additional data on the individual:
    if legacy_mode:
        logging.info("Initializing the NMEA stream mySQL connexion in legacy (MIBE) mode")
        db_stream = MysqlConnect_LegacyDB(host=host, port=port, usr=usr, pwd=pwd, db=dbname)
    else:
        logging.info("Initializing the NMEA stream mySQL connexion")
        db_stream = MysqlConnect(host=host, port=port, usr=usr, pwd=pwd, db=dbname)
    db_stream.connect()

    #------------------------------------------------------------------------------------------------------------------#
    # Start the MQTT client
    logging.info("Starting the MQTT broker connexion")
    broker_address = "localhost"
    client = mqtt.Client("nmea_stream")
    #client.on_connect = mqtt_on_connect # this does not work yet, check it out
    #client.mqtt_on_publish = mqtt_on_publish
    client.connect(broker_address)

    logging.info("Starting the MQTT broker thead")
    broadcast = threading.Thread(target=broadcast_detections_and_frequencies, args=(client, db_stream, stream_queue, passage_names, locations, port_dict))
    threads.append(broadcast)
    broadcast.start()
