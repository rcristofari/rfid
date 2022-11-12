# External dependencies:
import logging
import pymysql as pms
from functools import wraps
import sqlite3
import time


#----------------------------------------------------------------------------------------------------------------------#
# For the fixed system, we use a single MySQL connection:

class MysqlConnect:

    def __init__(self, usr, pwd, host='localhost', db='antavia_cro', port=3306):
        self.__usr = usr
        self.__pwd = pwd
        self.__host = host
        self.__dbname = db
        self.__port = int(port)
        self.__db = None
        self.__cursor = None

    def connect(self):
        try:
            self.__db = pms.connect(host=self.__host, user=self.__usr, passwd=self.__pwd, db=self.__dbname,
                                    port=self.__port)
            self.__cursor = self.__db.cursor()
            if self.__db.open:
                logging.info(f"Successfully established connection to {self.__dbname} on {self.__host}")
            else:
                logging.error(f"No connexion to {self.__dbname} on {self.__host}")
        except pms.OperationalError:
            logging.exception(f"Failed to connect to {self.__host}")

    def _reconnect(func):
        @wraps(func)
        def rec(self, *args, **kwargs):
            try:
                result = func(self, *args, **kwargs)
                return (result)
            except pms.err.OperationalError as e:
                logging.exception("Exception occurred (pymysql)")
                if e[0] == 2013:
                    self.connect()
                    result = func(self, *args, **kwargs)
                    return (result)

        return (rec)

    @_reconnect
    def penguin_exists(self, rfid):
        sql = f"SELECT rfid FROM birds WHERE birds.rfid = '{rfid}';"
        try:
            self.__cursor.execute(sql)
            rfid = self.__cursor.fetchone()
            if rfid:
                return (True, rfid[0])
            else:
                return (False, None)
        except Exception as ex:
            print(ex)
            logging.exception(ex)
            print("Error: unable to fetch data")

    @_reconnect
    def insert_auto(self, rfid):
        sql = f"INSERT INTO birds (rfid, name, rfid_date, rfid_stage) VALUES ('{rfid}', 'auto_{rfid}', '1970-01-01', 'N/A');"
        try:
            self.__cursor.execute(sql)
            self.__db.commit()
            return (self.__cursor.lastrowid)
        except pms.Error as e:
            error = "Error %d: %s" % (e.args[0], e.args[1])
            return (error)

    @_reconnect
    def insert_detection(self, antenna_id, rfid, dtime):
        sql = f"INSERT INTO detections (antenna_id, rfid, dtime, type) VALUES ({antenna_id + 1}, '{rfid}', '{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dtime))}', 'fixed');"
        print(sql)
        try:
            self.__cursor.execute(sql)
            self.__db.commit()
            return (self.__cursor.lastrowid)
        except pms.Error as e:
            error = "Error %d: %s" % (e.args[0], e.args[1])
            return (error)

    @_reconnect
    def nmea_sentence(self, rfid, dtime, antenna=""):
        date, hour = time.strftime('%d%m%y', time.localtime(dtime)), time.strftime('%H%M%S', time.localtime(dtime))

        name, sex, date_rfid, alarm = "", "", "", ""
        sql = f"SELECT name, sex, rfid_date, alarm FROM birds WHERE rfid = '{rfid}';"
        try:
            self.__cursor.execute(sql)
            data = self.__cursor.fetchone()
            if len(data) == 4:
                name, sex, date_rfid, alarm = data
        except Exception as ex:
            print(ex)
            logging.exception(ex)
            print("Error: unable to fetch data")
        return (f"$RFID,{antenna},{date},{hour},{rfid},{name},{date_rfid},{sex},{alarm}")


# ----------------------------------------------------------------------------------------------------------------------#
# Version with the MIBE schema:

class MysqlConnect_LegacyDB:

    def __init__(self, usr, pwd, host='localhost', db='antavia_cro', port=3306):
        self.__usr = usr
        self.__pwd = pwd
        self.__host = host
        self.__dbname = db
        self.__port = int(port)
        self.__db = None
        self.__cursor = None

    def connect(self):
        try:
            self.__db = pms.connect(host=self.__host, user=self.__usr, passwd=self.__pwd, db=self.__dbname,
                                    port=self.__port)
            self.__cursor = self.__db.cursor()
            if self.__db.open:
                logging.info(f"Successfully established connection to {self.__dbname} on {self.__host}")
            else:
                logging.error(f"No connexion to {self.__dbname} on {self.__host}")
        except pms.OperationalError:
            logging.exception(f"Failed to connect to {self.__host}")

    def _reconnect(func):
        @wraps(func)
        def rec(self, *args, **kwargs):
            try:
                result = func(self, *args, **kwargs)
                return (result)
            except pms.err.OperationalError as e:
                logging.exception("Exception occurred (pymysql)")
                if e[0] == 2013:
                    self.connect()
                    result = func(self, *args, **kwargs)
                    return (result)

        return (rec)

    @_reconnect
    def penguin_exists(self, rfid):
        sql = f"SELECT id FROM animaux WHERE animaux.identifiant_transpondeur = '{rfid}';"
        try:
            self.__cursor.execute(sql)
            id = self.__cursor.fetchone()
            if id:
                return (True, id[0])
            else:
                return (False, None)
        except Exception as ex:
            print(ex)
            logging.exception(ex)
            print("Error: unable to fetch data")

    @_reconnect
    def insert_auto(self, rfid):
        sql = f"INSERT INTO animaux (identifiant_transpondeur, nom, date_transpondage) VALUES ('{rfid}', 'auto_{rfid}', '1970-01-01');"
        try:
            self.__cursor.execute(sql)
            self.__db.commit()
            return (self.__cursor.lastrowid)
        except pms.Error as e:
            error = "Error %d: %s" % (e.args[0], e.args[1])
            return (error)

    @_reconnect
    def insert_detection(self, antenne_id, id, date_arrivee, date_depart):
        sql = f"INSERT INTO detections (antenne_id, animaux_id, date_arrivee, date_arrivee_ms, date_depart, date_depart_ms, analyse, modifie_a_la_main) VALUES ({antenne_id + 1}, {id}, '{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(date_arrivee))}', 0, '{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(date_depart))}', 0, 2, 0);"
        try:
            self.__cursor.execute(sql)
            self.__db.commit()
            return (self.__cursor.lastrowid)
        except pms.Error as e:
            error = "Error %d: %s" % (e.args[0], e.args[1])
            return (error)

    @_reconnect
    def update_departure_date(self, detection_id, departure_date):
        sql = f"UPDATE detections SET date_depart = '{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(departure_date))}' WHERE id = {detection_id};"

        try:
            self.__cursor.execute(sql)
            self.__db.commit()
        except pms.Error as e:
            error = "Error %d: %s" % (e.args[0], e.args[1])
            return (error)

    @_reconnect
    def nmea_sentence(self, rfid, dtime, antenna=""):
        date, hour = time.strftime('%d%m%y', time.localtime(dtime)), time.strftime('%H%M%S', time.localtime(dtime))

        name, sex, date_rfid, alarm = "", "", "", ""
        sql = f"SELECT nom, sexe, date_transpondage, son_suivi FROM animaux WHERE identifiant_transpondeur = '{rfid}';"
        try:
            self.__cursor.execute(sql)
            data = self.__cursor.fetchone()
            if len(data) == 4:
                name, sex, date_rfid, alarm = data
        except Exception as ex:
            print(ex)
            logging.exception(ex)
            print("Error: unable to fetch data")
        return (f"$RFID,{antenna},{date},{hour},{rfid},{name},{date_rfid},{sex},{alarm}")


# ----------------------------------------------------------------------------------------------------------------------#
# For the mobile system, we use two SQLite3 connections:

class Sqlite3Connect:

    def __init__(self, penguins_dbfile, detections_dbfile):
        # Open the penguin database connection:
        self._penguin_db = sqlite3.connect(penguins_dbfile)
        self._penguin_cursor = self._penguin_db.cursor()

        # Open the detections database connection:
        self._detect_db = sqlite3.connect(detections_dbfile)
        self._detect_cursor = self._detect_db.cursor()

    def __del__(self):
        self._penguin_db.close()
        self._detect_db.close()

    def nmea_sentence(self, rfid, dtime, antenna=""):
        date, hour = time.strftime('%d%m%y', time.localtime(dtime)), time.strftime('%H%M%S', time.localtime(dtime))
        name, sex, date_rfid, alarm = "", "", "", ""
        try:
            self._penguin_cursor.execute(f"SELECT name, date_rfid, sex, alarm FROM penguins WHERE rfid = '{rfid}';")
            values = self._penguin_cursor.fetchone()
            if values:
                name, date_rfid, sex, alarm = values

        except Exception as ex:
            logging.exception(ex)
            print("Error: unable to fetch data from penguins SQLite database")

        return f"$RFID,{antenna},{date},{time},{rfid},{name},{date_rfid},{sex},{alarm}"

    def insert_detection(self, rfid, dtime, antenna=""):
        dbdatetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dtime))
        sentence = self.nmea_sentence(rfid, time, antenna)
        try:
            self._detect_cursor.execute(
                f"INSERT INTO detections (antenna, date, rfid, nmea) VALUES ('{antenna}', '{dbdatetime}', '{rfid}', '{sentence}')")
            self._detect_db.commit()
        except Exception as ex:
            logging.exception(ex)
            print("Error: unable to insert data into the SQLite database")

    def insert_or_update_detection(selfself, rfid, dtime, antenna=""):
        pass
