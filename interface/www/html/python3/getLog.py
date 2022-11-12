#!/bin/python3
import sys
from datetime import datetime
startstr = sys.argv[1]
endstr = sys.argv[2]
try:
    start = datetime.strptime(startstr, "%Y-%m-%d")
    end = datetime.strptime(endstr, "%Y-%m-%d")
except ValueError:
    print("Invalid dates")
    quit()

record = False

with open("/home/pi/antavia_mobile/log/antavia.log", 'r') as logfile, open("/var/www/html/data/detections.txt", 'a') as ofile:

    ofile.write("#----------TECHNICAL LOG SECTION----------\n")

    for line in logfile:
        try:
            date = datetime.strptime(line.split(" ")[0], '%d-%b-%y')
            if date >= start and date <= end:
                record = True
                ofile.write(line)
            else:
                record = False
        except ValueError:
            if record:
                ofile.write(line)
