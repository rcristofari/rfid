import time, logging, subprocess
from datetime import datetime, timedelta

def hourly_logging(gps):
    
    now = datetime.now()
    next_hour = now.replace(second=0, microsecond=0, minute=0, hour=now.hour) + timedelta(hours=1)
    next_hour_posixct = time.mktime(next_hour.timetuple())

    while True:
        if next_hour_posixct - time.time() > 0:
            time.sleep(next_hour_posixct - time.time())
        else:
            logging.info("System is running")
            log_battery_params()
            if gps:
                gpstime = gps.get_time()
                if gpstime:
                    systemtime = datetime.now()
                    timediff = abs((gpstime - systemtime).total_seconds())
                    if timediff > 1: # If the GPS time differs from system time by more than 1 second, we update system time:
                        logging.info(f"Updated system time from GPS by {timediff} seconds")
                        subprocess.call(['date -s ' + datetime.strftime(gpstime, "%Y%m%d")], shell=True)
                        subprocess.call(['date -s ' + datetime.strftime(gpstime, "%H:%M:%S")], shell=True)
                    # Now check whether this time is in tune with the RTC time, and if needed update the RTC
                    sys_rtc_diff = abs(int(subprocess.check_output("/home/pi/antavia_mobile/sys_rtc_timediff.sh").decode("UTF-8")))
                    if sys_rtc_diff > 1:
                        subprocess.call("/home/pi/antavia_mobile/system_time_to_rtc.sh")
                        logging.info(f"Updated RTC time from system by {sys_rtc_diff} seconds")
                        
            now = datetime.now()
            next_hour = now.replace(second=0, microsecond=0, minute=0, hour=now.hour) + timedelta(hours=1)
            next_hour_posixct = time.mktime(next_hour.timetuple())
    
            
def log_battery_params():
    value = subprocess.check_output("/home/pi/antavia_mobile/get_battery_params.sh").decode("UTF-8")
    v_in, v_out, i_out, temp = value.strip("\n").split("\t")
    temp = temp.split("°")[0]
    logging.info(f"Battery {v_in}V, regulator supplying {v_out}V at {i_out}A, running at {temp}°C")

