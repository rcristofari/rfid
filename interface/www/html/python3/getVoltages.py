#!/bin/python3
from datetime import datetime
import json

XY = []

with open("/home/pi/antavia_mobile/log/antavia.log", 'r') as ifile:
    for line in ifile:
        if "Battery" in line:
            dtime = datetime.strptime(line.split(" - ")[0].strip(" "), '%d-%b-%y %H:%M:%S').timestamp()*1000
            now = datetime.now().timestamp() * 1000
            if now - dtime <= 14*24*3600*1000:
                u = float(line.split(" ")[8].strip(",").strip("V"))
                xy = {'dtime':dtime, 'V':u}
                XY.append(xy)

json_object = json.dumps({'voltage':XY}, indent=4)

with open("/var/www/html/data/battery.js", 'w') as jfile:
    jfile.write("var jsonfile = ")
    jfile.write(json_object)
    jfile.write(";")
