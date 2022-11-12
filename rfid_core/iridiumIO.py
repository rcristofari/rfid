import time
#----------------------------------------------------------------------------------------------------------------------#
# trans is the direction: 0 for sea-to-sea, 1 for sea-to-land, 2 for land-to-sea, 3 for land-to-land
# = binary 00, 01, 10, 11. Default on simplex antennas is 0

class RockBlock():

    def __init__(self, iridium_port):
        self._device = serial.Serial(iridium_port, baudrate=19200, timeout=30.0)
        
    def __del__(self):
        self._device.close()

    def encode_bin_message(self, dtime, rfid, trans=0):
        ltime = time.localtime(dtime)
        ymin = ltime[7] * 24 * 60 + ltime[3] * 60 + ltime[4]
        ymin_bin = f'{ymin:020b}'  # time is the first 20 bits
        trans_bin = f'{trans:02b}'  # transition direction is the next 2 bits
        rfidcode = {"A 00000 0 964 ": "0", "A 00000 0 999 ": "1", "R 0000 0000": "2"}
        shortrfid = int(rfidcode[rfid[:-12]] + rfid[-12:])
        rfid_bin = f'{shortrfid:042b}'  # rfid number is the last 42 bits
        msg = int(ymin_bin + trans_bin + rfid_bin, 2)
        binary = msg.to_bytes(8, "little")
        return binary
    
    def make_sbd(self, messages):
        # There needs to be exactly 6 messages !
        bin_messages = b''
        for i in range(6):
            bin_messages += self.encode_bin_message(messages[i][0], messages[i][1], messages[i][2])
        checksum = self.make_checksum(bin_messages)
        clear_to_tx = bin_messages + checksum
        return clear_to_tx
        
    def make_checksum(self, bin_messages):
        checksum = 0
        for c in bin_messages:
            checksum += c
        return bytes([checksum >> 8, checksum & 0xFF]) 
            
    def tx_bin_message(self, msg):
        self._device.write(b"AT+SBDWB=48\r") # write bin to outbound buffer
        self._device.readline()
        answer = self._device.readline().decode("UTF-8")
        print(answer)
        if answer == "READY\r\n":
            self._device.write(msg + b"\r")
            self._device.readline()
            status = int(self._device.readline().decode("UTF-8"))
            self._device.readline()
            answer = self._device.readline().decode("UTF-8")
            print(answer)
            if answer == "OK\r\n":
                success = False
                while not success:
                    self._device.write(b"AT+SBDIX\r") # transmit data
                    self._device.readline().decode("UTF-8")   ## CHECK TX STATUS, keep trying or not
                    self._device.readline().decode("UTF-8")
                    
rb = RockBlock("/dev/ttyUSB0")
    # suggested retry logic:
    # retry withn random time 0-5 sec (repeat 2x)
    # repeat with random time 0-30 sec (repeat 2x)
    # increment delay to 5 minutes and do periodic retries

# Decode an 8-byte message into POSIXct datetime and RFID number
def decode_bin_message(binary, year=None):
    as_int = int.from_bytes(binary, "little")
    # decode the RFID number
    rfidcode = {"0": "A 00000 0 964 ", "1": "A 00000 0 999 ", "2": "R 0000 0000"}
    rfidb = f'{int(bin(as_int)[-42:], 2):013}'
    rfid = rfidcode[rfidb[0]] + rfidb[1:]
    # decode the transition
    trans = int(bin(as_int)[-44:-42], 2)
    # decode the time into POSIXct
    ymin = int(bin(as_int)[:20], 2)
    if not year:
        year = time.localtime(time.time())[0]
    yday = ymin // (24*60)
    hoursmin = ymin % (24*60)
    hours = hoursmin // 60
    mins = hoursmin % 60
    dtime = time.mktime(time.strptime(f"{year}:{yday}:{hours}:{mins}", "%Y:%j:%H:%M"))
    return dtime, rfid, trans

def decode_sbd_from_file(sbd_file, year=None):
    out = []
    with open(sbd_file, 'rb') as ifile:
        while byte := ifile.read(8):
            dtime, rfid, trans = decode_bin_message(byte, year=year)
            out.append([dtime, rfid, trans])
    return out

# This gives exactly 48 bytes ! ## NOTE ! 1 credit = 50 bytes, but 1 SBD can contain up to 340 bytes, if needed.
# Note there will be an automatic 2-byte checksum
#with open("/home/robin/binsbd", 'wb') as ofile:
#    ofile.write(encode_bin_message(time.time(), "A 00000 0 964 001002458394", 0))
#    ofile.write(encode_bin_message(time.time(), "A 00000 0 964 023004758304", 0))
#    ofile.write(encode_bin_message(time.time(), "A 00000 0 999 111005168537", 1))
#    ofile.write(encode_bin_message(time.time(), "A 00000 0 964 001058719258", 0))
#    ofile.write(encode_bin_message(time.time(), "A 00000 0 964 038168987165", 3))
#    ofile.write(encode_bin_message(time.time(), "R 0000 0000768245982375", 2))


bm = b''
bm += encode_bin_message(1, time.time(), "A 00000 0 964 001002458394", 0)
bm += encode_bin_message(1, time.time(), "A 00000 0 964 023004758304", 0)
bm += encode_bin_message(1, time.time(), "A 00000 0 999 111005168537", 1)
bm += encode_bin_message(1, time.time(), "A 00000 0 964 001058719258", 0)
bm += encode_bin_message(1, time.time(), "A 00000 0 964 038168987165", 3)
bm += encode_bin_message(1, time.time(), "R 0000 0000768245982375", 2)

messages = [(time.time(), "A 00000 0 964 001002458394", 0), (time.time(), "A 00000 0 964 023004758304", 0), (time.time(), "A 00000 0 999 111005168537", 1),
            (time.time(), "A 00000 0 964 001058719258", 0), (time.time(), "A 00000 0 964 038168987165", 3), (time.time(), "R 0000 0000768245982375", 2)]