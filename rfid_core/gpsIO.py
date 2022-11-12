from datetime import datetime
import serial, logging, time

class GPSDevice():
    
    def __init__(self, gps_port):
        self._gps_device = serial.Serial(gps_port, baudrate = 9600, timeout = 3.0)
        self._gps_device.flush()
        try:
            self._gps_device.write(b'$PMTK353,1,0,0,0,0*2A\r\n') # Set all sentences to $GP prefix
            self._gps_device.write(b"$PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*29\r\n") # Output only $GPRMC
            self._gps_device.write(b'$PMTK220,1000*1F\r\n') # Set frequency to 1Hz
            self._isLegacyGps = False
        except OSError:
            logging.warning("Unable to set GPS device parameters")
            self._isLegacyGps = True

    def standby(self):
        # Go to sleep mode
        if not self._isLegacyGps:
            self._gps_device.write(b"$PMTK161,0*28\r\n")
        
    def wakeup(self):
        # Resume at 1Hz
        if not self._isLegacyGps:
            self._gps_device.write(b'$PMTK220,1000*1F\r\n')

    def get_time(self, timeout = 180):
        # Note that the GPS device needs to have a timeout >> refresh frequency
        self.wakeup()
        start_time = time.time()
        buffer = self._gps_device.readline().decode("UTF-8")
        values = buffer.split(",")
        while not (buffer.startswith("$GPRMC") and values[2] == "A"):
            buffer = self._gps_device.readline().decode("UTF-8")
            values = buffer.split(",")
            if time.time() - start_time > timeout:
                break
            
        if buffer.startswith("$GPRMC") and values[2] == "A":
            logging.info("Obtained a valid GPS fix")
            return datetime.strptime(values[9]+values[1].split(".")[0], "%d%m%y%H%M%S")
        else:
            logging.info("Failed to obtain a valid GPS fix")
            return None
    
    def readline(self):
        buffer = self._gps_device.readline().decode("UTF-8")
        return(buffer)
