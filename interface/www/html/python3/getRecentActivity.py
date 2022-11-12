#!/bin/python3
from datetime import datetime
last_7_days = 0
last_24_hours = 0

with open("/var/www/antavia_mobile.txt", 'r') as ifile:
    for line in ifile:
        if line.startswith("$RFID"):
            values = line.split(",")
            time = datetime.strptime(values[2]+values[3], "%Y%m%d%H%M%S")
            delta = (datetime.now() - time).total_seconds()
            if delta <= 604800:
                last_7_days += 1
            if delta <= 86400:
                last_24_hours += 1
print("There have been %d detections during the past 7 days, including %d during the last 24 hours." % (last_7_days, last_24_hours))
