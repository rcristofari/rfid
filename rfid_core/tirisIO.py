import re, sys, time, logging, serial
#import RPi.GPIO as GPIO


########################################################################################################################
# The TIRIS reader object, containing core method reading a TRX on the serial device

class TirisReader():
    'A TIRIS reader object, connected as a serial device. Allows to read RFID tags and start a continuous monitoring process.'

    def __init__(self, port, baudrate=9600, timeout=1.0, n_antennas=1, muxMSB=26, muxLSB=19, mode="SYNCHRO", penguin_is_sleeping=False):
        self._device = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        self._n_antennas = n_antennas
        self._muxMSB = muxMSB
        self._muxLSB = muxLSB
        if mode == "SYNCHRO":
            self._sync = True
        elif mode == "SLAVE":
            self._sync = False
        else:
            raise Exception("TIRIS mode can only be SYNCHRO or SLAVE")
        
    def __del__(self):
        self._device.close()

    # Check that this is indeed a TIRIS reader
    def identify(self):
        if not self._sync:
            self._device.write(b'X\r\n')
            time.sleep(0.01)
            answer = self._device.readline().decode("UTF-8").strip("\n").strip("\r")
            if answer.startswith("X"):
                return True
        else:
            raise Exception("Identification only works in SLAVE mode")

    # Perform a read cycle in SLAVE mode
    def query(self):
        if not self._sync:
            self._device.write(b'X\r\n')  # send the EXECUTE command to the reader
            #time.sleep(0.01)  # give it time to respond - check if 10 ms are sufficient, increase if necessary !
            answer = self._device.readline().decode("UTF-8").strip("\n").strip("\r")
            if re.search(r"XA 00000 0 [0-9]{3} [0-9]{12}", answer) or re.search(r"XR 0000 [0-9]{16}", answer):
                return True, self._device.name, None, time.time(), answer[1:]
            else:
                return False, self._device.name, None, time.time(), None, None
        else:
            raise Exception("In SYNCHRO mode, use the 'read' method instead of 'query'")

    # Perform a read cycle in SYNCHRO mode
    def read(self):
        if self._sync:
            answer = self._device.readline().decode("UTF-8").strip("\n").strip("\r")
            if re.search(r"LA 00000 0 [0-9]{3} [0-9]{12}", answer) or re.search(r"LR 0000 [0-9]{16}", answer):
                return True, self._device.name, time.time(), answer[1:]
            elif answer.startswith("L"):
                return False, self._device.name, time.time(), None
        else:
            raise Exception("In SLAVE mode, use the 'query' method instead of 'read'")

    # Switch the multiplexer to a given antenna
    def switchMUX(self, to_antenna):
        muxCode = {0: (0, 0), 1: (0, 1), 2: (1, 0), 3: (1, 1)}
        GPIO.output(self._muxMSB, muxCode[to_antenna][0])
        GPIO.output(self._muxLSB, muxCode[to_antenna][1])

    # Start an open-ended monitoring process
    def monitor(self, detection_queue, pulse=500, display=None):

        this_antenna = 0  # we always start on the first antenna
        previous_rfid = [None, None, None, None]  # No previous detections at the start
        previous_detection_time = [None, None, None, None]  # Last reading time for that TRX, POSIXct (for repeated detection avoidance)

        # Pulse management loop:
        while True:
            nextTime = time.time() + (pulse / 1000)
            # Send a read order and read the buffer
            detection = self.query()

            if detection:  # a message has been received from the TIRIS
                # Update the message to include antenna number
                detection = (detection[0], detection[1], this_antenna, detection[3], detection[4])

                if detection[0]:  # the message contains an RFID number
                    print(detection, flush=True)
                    
                    if display:
                        display.detection(detection[4], detection[3], detection[2])
                    
                    if (detection[4] != previous_rfid[this_antenna]) or (time.time() - previous_detection_time[this_antenna]) > 600: # it's either a new penguin, or 10 minutes have elapsed without detection
                        detection_queue.put(detection)  # we add the detection to the queue for processing
                        # we update the info to check the next detection
                        previous_rfid[this_antenna], previous_detection_time[this_antenna] = detection[4], detection[3]

            # Finally, witch the MUX to the next antenna
            if self._n_antennas > 1:
                if this_antenna < (self._n_antennas - 1):
                    this_antenna += 1
                    
                else:
                    this_antenna = 0
                self.switchMUX(this_antenna)
             
            time.sleep(max(0, nextTime - time.time()))
            

    def listen(self, db_queue, stream_queue, pulse=50):
        previous_rfid, previous_arrival_time = None, None

        # Pulse management:
        while True:
            nextTime = time.time() + (pulse / 1000)
            detection = self.read()  # read the TIRIS buffer

            if detection:  # a message has been received from the TIRIS
                stream_queue.put(detection)  # in any case, we add it to the streaming queue
                if detection[0]:  # the message contains an RFID number
                    if detection[3] != previous_rfid:  # it's a new penguin
                        db_queue.put(detection)  # we add the detection to the queue for processing
                        previous_rfid, previous_arrival_time = detection[3], detection[2]  # we update the info to check the next detection
                    else:  # it's the same penguin than the last detection
                        # we update this as the latest known detection time for this penguin
                        previous_arrival_time = detection[2]
                        if time.time() - previous_arrival_time > 120:  # it hadn't been seen for over 2 minutes
                            db_queue.put(detection)  # we record it as a new detection
            time.sleep(max(0, nextTime - time.time()))