#!/usr/bin/python3
#import RPi.GPIO as GPIO
import os, serial, subprocess, time, logging
from datetime import datetime
from rfid_core.lcd import *

# ----------------------------------------------------------------------------------------------------------------------#

def legacy_scan_devices():
    logging.info("Scanning USB devices")
    tiris, gps, iridium = None, None, None
    for TestPort in range(4):
        print("Searching for device on ttyUSB" + str(TestPort))
        if os.path.exists('/sys/bus/usb-serial/devices/ttyUSB' + str(TestPort)):
            print("Device connected to ttyUSB" + str(TestPort))
            if os.path.exists('/sys/bus/usb-serial/devices/ttyUSB%s/uevent' % str(TestPort)):
                portFile = open("/sys/bus/usb-serial/devices/ttyUSB%s/uevent" % str(TestPort), "r")
                infile = portFile.read(11)
                if infile in ("DRIVER=pl23", "DRIVER=ftdi", "DRIVER=navman"):
                    # Initiate a connexion and test device identity.
                    logging.info(f"TIRIS device found on /dev/ttyUSB{TestPort}")
                    print(f"TIRIS device found on /dev/ttyUSB{TestPort}")
                    tiris = TestPort
                elif infile == "DRIVER=navm":
                    # Initiate a connexion and test device identity.
                    logging.info(f"GPS device found on /dev/ttyUSB{TestPort}")
                    print(f"GPS device found on /dev/ttyUSB{TestPort}")
                    gps = TestPort
                elif infile == "DRIVER=XX":
                    # Initiate a connexion and test device identity.
                    logging.info(f"Iridium device found on /dev/ttyUSB{TestPort}")
                    print(f"Iridium device found on /dev/ttyUSB{TestPort}")
                    iridium = TestPort
                portFile.close()
    return {"TIRIS": tiris, "GPS": gps, "IRIDIUM": iridium} #, [list of Serial connexion objects]


def scan_devices():
    logging.info("Scanning USB devices")
    tiris, gps, iridium = None, None, None
    
    for TestPort in range(4):
        print("Searching for device on ttyUSB" + str(TestPort))
        
        if os.path.exists('/sys/bus/usb-serial/devices/ttyUSB' + str(TestPort)):
            
            print("Device connected to ttyUSB" + str(TestPort))
            
            if os.path.exists('/sys/bus/usb-serial/devices/ttyUSB%s/uevent' % str(TestPort)):
                
                portFile = open("/sys/bus/usb-serial/devices/ttyUSB%s/uevent" % str(TestPort), "r")
                infile = portFile.read(11)
                portFile.close()
                
                if infile in ("DRIVER=pl23", "DRIVER=ftdi"):
                    # Initiate a connexion and test device identity.
                    serialdevice = serial.Serial(f"/dev/ttyUSB{TestPort}", baudrate=9600, timeout=1.0)
                    # Send an execute command to check if it's answering as a TIRIS
                    serialdevice.write(b'X\r\n')
                    buffer = serialdevice.readline().decode("UTF-8")
                    if buffer.startswith("X"):
                        logging.info(f"TIRIS device found on /dev/ttyUSB{TestPort}")
                        print(f"TIRIS device found on /dev/ttyUSB{TestPort}")
                        tiris = TestPort
                        
                    else:
                        serialdevice.readline() # this line may be incomplete
                        buffer = serialdevice.readline().decode("UTF-8")
                        if buffer.startswith("$G"):
                            logging.info(f"GPS device found on /dev/ttyUSB{TestPort}")
                            print(f"GPS device found on /dev/ttyUSB{TestPort}")
                            gps = TestPort
                            serialdevice.close()
                        
                        # Now test if it may be the RockBlock:
                        else:
                            serialdevice = serial.Serial(f"/dev/ttyUSB{TestPort}", baudrate=19200, timeout=1.0)
                            serialdevice.write(b"AT\r\n")
                            serialdevice.readline().decode("UTF-8")
                            serialdevice.readline().decode("UTF-8")
                            buffer = serialdevice.readline().decode("UTF-8")
                            if buffer == "OK\r\n":
                                logging.info(f"Iridium device found on /dev/ttyUSB{TestPort}")
                                print(f"Iridium device found on /dev/ttyUSB{TestPort}")
                                iridium = TestPort
                            
                    serialdevice.close()
                    
                elif infile == "DRIVER=navm":
                    logging.info(f"Legacy (CatTrack) GPS device found on /dev/ttyUSB{TestPort}")
                    print(f"Legacy (CatTrack) GPS device found on /dev/ttyUSB{TestPort}")
                    gps = TestPort
                    
    return {"TIRIS": tiris, "GPS": gps, "IRIDIUM": iridium} #, [list of Serial connexion objects]


# ----------------------------------------------------------------------------------------------------------------------#
## SKIP ALL THAT. JUST PHYSICALLY UNPLUG THE GPS TO SKIP IT, IT WILL MAKE EVERYTHING SIMPLER.
def get_gps_fix(GPSport, timeout, USE_LCD=False, display=None):
    # timeout: time (in minutes) waiting for a fix before proceeding without a fix
    startTime = time.time()
    monitorTime_0 = time.time()

    if USE_LCD:
        TextToLCD(display, " GETTING GPS FIX", datetime.strftime(datetime.now(), "%H:%M-%S - waiting"), "Press HALT to",
                  "skip and proceed")

    keepTrying = True
    if GPSport:
        while keepTrying is True:
            if GPIO.input(16) == 0:
                print("No GPS fix, proceed with last known time")
                if USE_LCD:
                    TextToLCD(display, "No GPS fix, system", "proceeds w/o GPS.", "Note relative time:",
                              datetime.strftime(datetime.now(), "%Y%m%d %H:%M:%S"))
                keepTrying = False
                return (["# NO GPS FIX, PROCEEDING WITH LATEST KNOWN TIME - INTERPRET DATA WITH CAUTION\n", 0])
            else:
                GPSport.flushInput()
                GPSRX = GPSport.readline().decode("UTF-8")
                while not GPSRX.startswith('$GPRMC'):
                    try:
                        GPSRX = GPSport.readline().decode("UTF-8")
                    except SerialException:
                        GPSRX = ""
                line = GPSRX.split(",")
                if line[2] == "A":
                    try:
                        GPSdate = datetime.strptime(line[9], "%d%m%y")
                        GPStime = datetime.strptime(line[1][:6], "%H%M%S")
                        # Set system time:
                        print(GPSRX)
                        subprocess.call(['date -s ' + datetime.strftime(GPSdate, "%Y%m%d")], shell=True)
                        subprocess.call(['date -s ' + datetime.strftime(GPStime, "%H:%M:%S")], shell=True)
                        keepTrying = False
                        return ([GPSRX, 1])
                    except ValueError:
                        pass
                elif time.time() - startTime > (60 * timeout):
                    print("No GPS fix, proceed with last known time")
                    if USE_LCD:
                        TextToLCD(display, "No GPS fix, system", "proceeds w/o GPS.", "Note relative time:",
                                  datetime.strftime(datetime.now(), "%Y%m%d %H:%M:%S"))

                    keepTrying = False
                    return (["# NO GPS FIX, PROCEEDING WITH LATEST KNOWN TIME - INTERPRET DATA WITH CAUTION\n", 0])
                else:
                    monitorTime_1 = time.time()
                    if monitorTime_1 - monitorTime_0 > 10:
                        monitorTime_0 = monitorTime_1
                        if USE_LCD:
                            TextToLCD(display, " GETTING GPS FIX",
                                      datetime.strftime(datetime.now(), "%H:%M-%S - waiting"), "Press HALT to",
                                      "skip and proceed")
                        print(datetime.strftime(datetime.now(),
                                                "%H:%M-%S --- Waiting for GPS fix, press HALT to skip GPS sync"))
    else:
        if USE_LCD:
            TextToLCD(display, "NO GPS RX, system", "proceeds w/o GPS.", "Note relative time:",
                      datetime.strftime(datetime.now(), "%Y%m%d %H:%M:%S"))
        return (["# NO GPS FOUND, PROCEEDING WITH LATEST KNOWN TIME - INTERPRET DATA WITH CAUTION\n", 0])