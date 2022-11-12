import string
import time
from datetime import datetime
import logging

#----------------------------------------------------------------------------------------------------------------------#
# Read the path file

def read_paths(path, system="mobile"):

    if system == "mobile":
        log_file, serial_conf_file, penguins_dbfile, detections_dbfile, detections_txtfile, fontfile = None, None, None, None, None, None
        with open(path, 'r') as ifile:
            for line in ifile:
                if not line.startswith("#") and "=" in line:
                    param, value = line.strip("\n").split("=")
                    if param == "LOG":
                        log_file = value
                    elif param == "SERIAL":
                        serial_conf_file = value
                    elif param == "PENGUINDB":
                        penguins_dbfile = value
                    elif param == "RFIDDB":
                        detections_dbfile = value
                    elif param == "RFIDTXT":
                        detections_txtfile = value
                    elif param == "LCDFONT":
                        fontfile = value
                    else:
                        logging.warning(f"Unknown parameter {param} in {path} file.")
                        raise Exception(f"Unknown parameter {param} in the mysql.conf configuration file")
        if not log_file and serial_conf_file and penguins_dbfile and detections_dbfile and detections_txtfile and fontfile:
            logging.error(f"{path} file is incomplete.")

        return log_file, serial_conf_file, penguins_dbfile, detections_dbfile, detections_txtfile, fontfile

    elif system == "fixed":

        log_file, serial_conf_file, mysql_conf_file = None, None, None
        with open(path, 'r') as ifile:
            for line in ifile:
                if not line.startswith("#") and "=" in line:
                    param, value = line.strip("\n").split("=")
                    if param == "LOG":
                        log_file = value
                    elif param == "SERIAL":
                        serial_conf_file = value
                    elif param == "MYSQL":
                        mysql_conf_file = value
                    else:
                        logging.warning(f"Unknown parameter {param} in {path} file.")
                        raise Exception(f"Unknown parameter {param} in the mysql.conf configuration file")

        if not log_file and serial_conf_file and mysql_conf_file:
            logging.error(f"{path} file is incomplete.")

        return log_file, serial_conf_file, mysql_conf_file


#----------------------------------------------------------------------------------------------------------------------#
# Read the mobile antenna configuration file

def read_settings(file):
    antenna_name, base_freq, n_antennas, use_lcd = "AntaviaMobile", 2, 1, True
    with open(file, 'r') as ifile:
        for line in ifile:
            args = line.strip("\n").split(":")
            if args[0] == "antenna_name":
                antenna_name = str(args[1][1:])
            elif args[0] == "base_freq":
                try:
                    base_freq = int(args[1][1:])
                except ValueError:
                    base_freq = 2
            elif args[0] == "n_antennas":
                try:
                    n_antennas = int(args[1][1:])
                except ValueError:
                    n_antennas = 1
            elif args[0] == "use_lcd":
                if args[1][1:] == "False":
                    use_lcd = False
                else:
                    use_lcd = True
    return antenna_name, base_freq, n_antennas, use_lcd


#----------------------------------------------------------------------------------------------------------------------#
# Read and parse the MySQL configuration file

def read_mysql_conf(path):
    host, port, usr, pwd, db = None, None, None, None, None
    with open(path, 'r') as ifile:
        for line in ifile:
            if not line.startswith("#") and "=" in line:
                param, value = line.strip("\n").split("=")
                if param == "host":
                    host = value
                elif param == "port":
                    port = int(value)
                elif param == "usr":
                    usr = value
                elif param == "pwd":
                    pwd = value
                elif param == "db":
                    db = value
                else:
                    raise(f"Unknown parameter {param} in the mysql.conf configuration file")
                    logging.warning(f"Unknown parameter {param} in {path} file.")
    if not host and port and usr and pwd and db:
        logging.error(f"{path} file is incomplete.")

    else:
        logging.info(f"Successfully loaded mySQL configuration file {path}.")
        return(host, port, usr, pwd, db)


#----------------------------------------------------------------------------------------------------------------------#
# Read and parse the serial configuration file
def read_serial_conf(path):
    nReaders = 0
    portPaths = []
    passageNames = []
    locations = []
    baudrates = []
    timeouts = []

    with open(path, 'r') as ifile:
        for line in ifile:
            if not line.startswith("#"):
                row = line.strip("\n").split(":")
                if len(row) != 6:
                    logging.error("Serial configuration file is malformed. Each line must contain id:path:baudrate:timeout:name")
                    raise Exception("Serial configuration file is malformed. Each line must contain id:path:baudrate:timeout:name")

                else:
                    nReaders += 1
                    portPaths.append(row[1])
                    try:
                        baudrates.append(int(row[2]))
                    except ValueError:
                        logging.warning(f"No valid baudrate specified for port {row[1]}. Using default value of 9600")
                        baudrates.append(9600)
                    try:
                        timeouts.append(float(row[3]))
                    except ValueError:
                        logging.warning(f"No valid timeout specified for port {row[1]}. Using default value of 1.0")
                        timeouts.append(9600)
                    if row[4] != "":
                        passageNames.append(row[4])
                    if row[5] != "":
                        locations.append(row[5])
                    else:
                        passageNames.append("antenna_%d" % nAntennas)

    portDict, portPaths, passageNames, baudrates, timeouts = dict(
        zip(portPaths, [x for x in range(nReaders)])), tuple(portPaths), tuple(passageNames), tuple(
        baudrates), tuple(timeouts)

    if nReaders > 0:
        logging.info(f"Successfully loaded serial configuration file {path}. Initializing {nReaders} antennas.")
    else:
        logging.error(f"No antennas defined in {path}")

    return nReaders, portDict, portPaths, passageNames, locations, baudrates, timeouts

