import queue
import logging
from rfid_core.dbIO import *

#----------------------------------------------------------------------------------------------------------------------#
# For the mobile system

def handle_detections_mobile(dbcon, detection_queue, nmea_queue, detections_txtfile, antenna_name):

    while True:
        detection = detection_queue.get()
        status, antenna, antenna_nr, dtime, rfid = detection
        antenna_id = f"{antenna_name}_{antenna_nr}"
        if not status:
            logging.debug("A non-rfid serial message has been routed to the database (and rejected).")
            raise Exception("Only valid detections can be inserted into the database")
        else:
            # Insert into the SQLite database
            dbcon.insert_detection(rfid, dtime, antenna_id)   # insert that string with metadata into SQLITE
            sentence = dbcon.nmea_sentence(rfid, dtime, antenna_id)
            nmea_queue.put(sentence)  # Add the string to the queue for broadcasting.

            # Add the sentence to the raw text file for redundancy
            txtfile = open(detections_txtfile, 'a+')
            txtfile.write(sentence + '\n')
            txtfile.close()

            #if display:
            #    display.detection(rfid, dtime, antenna_nr)

#----------------------------------------------------------------------------------------------------------------------#
# For the fixed system

def handle_detections_fixed(dbcon, db_queue, port_dict, legacy_mode=False):

    while True:
        detection = db_queue.get()
        print(f"-- Processing detection {detection[3]} at {detection[2]}")

        status, antenna, time, rfid = detection
        antenna_id = port_dict[antenna]
        if not status:
            logging.debug("A non-rfid serial message has been routed to the database (and rejected). This should not happen.")
            raise Exception("Only valid detections can be inserted into the database")
        else:
            if legacy_mode:
                this_penguin_exists, this_penguin_id = dbcon.penguin_exists(rfid)
                if not this_penguin_exists:  # the penguin is not known in the database yet
                    this_penguin_id = dbcon.insert_auto(rfid)
                dbcon.insert_detection(antenna_id, this_penguin_id, time, time)
            else:
                this_penguin_exists, this_penguin_rfid = dbcon.penguin_exists(rfid)
                if not this_penguin_exists:  # the penguin is not known in the database yet
                    this_penguin_rfid = dbcon.insert_auto(rfid)
                dbcon.insert_detection(antenna_id, this_penguin_rfid, time)