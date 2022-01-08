import os
import sqlite3
from datetime import datetime

from data.translator import Translator
from data.versicle import Versicle
from data.weather import Weather
from data.web_search import WebSearch
from util.const import CACHE, get_engine_by_name, get_request_type_by_name
from util.logger import SENT_TO_LOG

DB_FILE = os.path.join(CACHE, "cache.db")

def CREATE_TABLES():
    if not os.path.exists(DB_FILE):
        try:
            os.mkdir(CACHE)
        except:
            pass
        try:
            with open(DB_FILE, "w") as db:
                db.write("")
        except Exception as e:
            msg = f"No se pudo crear el archivo DB > {e.args}"
            print(msg)
        # creo las tablas con sus columnas
        with sqlite3.connect(DB_FILE) as temp_conexion:
            temp_cursor = temp_conexion.cursor()
            # traductor
            query_translator = """CREATE TABLE "main"."translator" (
      "datetime" TEXT NOT NULL,
      "text_to_translate" TEXT,
      "from_language" TEXT,
      "to_language" TEXT,
      "traduction" TEXT,
      PRIMARY KEY ("datetime")
    );"""
            temp_cursor.execute(query_translator)
            # clima
            query_weather = """CREATE TABLE "main"."weather" (
      "datetime" TEXT NOT NULL,
      "temp" REAL,
      "max_temp" REAL,
      "min_temp" REAL,
      "feels_like" REAL,
      "weather" TEXT,
      "icon" TEXT,
      "wind" REAL,
      "pressure" INTEGER,
      "humidity" INTEGER,
      "country" TEXT,
      "long" REAL,
      "lat" REAL,
      "sea_lvl" REAL,
      "ground_lvl" REAL,
      "sunrise" TEXT,
      "sunset" TEXT,
      PRIMARY KEY ("datetime")
    );"""
            temp_cursor.execute(query_weather)
            # versiculo
            query_versicle = """CREATE TABLE "main"."versicle" (
      "datetime" TEXT NOT NULL,
      "text" TEXT,
      "verse" TEXT,
      PRIMARY KEY ("datetime")
    );"""
            temp_cursor.execute(query_versicle)
            # web search
            query_web = """CREATE TABLE "main"."web_search" (
                  "datetime" TEXT NOT NULL,
                  "founded" TEXT,
                  "criterion" TEXT,
                  "url" TEXT,
                  "engine" TEXT,
                  "request_type" TEXT,
                  "attachment" TEXT,
                  "elapsed_time" TEXT,
                  "size" REAL,
                  PRIMARY KEY ("datetime")
                );"""
            temp_cursor.execute(query_web)
            # guardar cambios
            temp_conexion.commit()
            # cerrar conexion y cursor
            temp_cursor.close()

def INSERT_WEATHER(weather:Weather):
    try:
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()
        query = """INSERT INTO "main"."weather" ("datetime", "temp", "max_temp", "min_temp", "feels_like", "weather", "icon", "wind", "pressure", "humidity", "country", "long", "lat", "sea_lvl", "ground_lvl", "sunrise", "sunset") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
        cur.execute(query, [weather.datetime, weather.temp, weather.max_temp, weather.min_temp, weather.feels_like, weather.weather, weather.icon, weather.wind, weather.pressure, weather.humidity, weather.country, weather.long, weather.lat, weather.sea_lvl, weather.ground_lvl, weather.sunrise, weather.sunset])
        con.commit()
    except sqlite3.Error as e:
        print(e.args)
        SENT_TO_LOG(f"Agregando datos del clima a la DB {e.args}", "ERROR")

def INSERT_TRANSLATION(translator:Translator):
    try:
        print(type(translator.criterion))
        with sqlite3.connect(DB_FILE) as con:
            print(translator.criterion)
            cur = con.cursor()
            query = """INSERT INTO "main"."translator" ("datetime", "text_to_translate", "from_language", "to_language", "traduction") VALUES (?, ?, ?, ?, ?);"""
            cur.execute(query, [translator.creation_date, translator.criterion, translator.from_[0], translator.to_[0], translator.translation])
            con.commit()
    except sqlite3.Error as e:
        print(e.args)
        SENT_TO_LOG(f"Agregando datos del traductor a la DB {e.args}", "ERROR")

def INSERT_VERSICLE(versicle:Versicle):
    try:
        with sqlite3.connect(DB_FILE) as con:
            cur = con.cursor()
            query = """INSERT INTO "main"."versicle" ("datetime", "text", "verse") VALUES (?, ?, ?);"""
            cur.execute(query, [versicle.creation_date, versicle.text, versicle.verse])
            con.commit()
    except sqlite3.Error as e:
        print(e.args)
        SENT_TO_LOG(f"Agregando datos del versiculo a la DB {e.args}", "ERROR")

def INSERT_WEB_SEARCH(web_search:WebSearch):
    try:
        with sqlite3.connect(DB_FILE) as con:
            cur = con.cursor()
            query = """INSERT INTO "main"."web_search" ("datetime", "founded", "criterion", "url", "engine", "request_type", "attachment", "elapsed_time", "size") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);"""
            cur.execute(query, [web_search.creation_date, str(web_search.FOUNDED), web_search.criterion, web_search.url, web_search.engine.name, web_search.request_type.name, web_search.path_attachment, web_search.elapsed_time, web_search.size])
            con.commit()
    except sqlite3.Error as e:
        print(e.args)
        SENT_TO_LOG(f"Agregando datos de la búsqueda a la DB {e.args}", "ERROR")

def UPDATE_WEB_SEARCH(web_search:WebSearch):
    try:
        with sqlite3.connect(DB_FILE) as con:
            cur = con.cursor()
            query = """UPDATE "main"."web_search" SET "founded" = ?, "attachment" = ?, "elapsed_time" = ?, "size" = ? WHERE "datetime" = ?;"""
            cur.execute(query, [str(web_search.FOUNDED), web_search.path_attachment, web_search.elapsed_time, web_search.size, web_search.creation_date])
            con.commit()
    except sqlite3.Error as e:
        print(e.args)
        SENT_TO_LOG(f"Actualizando datos de la búsqueda a la DB {e.args}", "ERROR")

def GET_HISTORY(search=""):
    try:
        with sqlite3.connect(DB_FILE) as con:
            cur = con.cursor()
            query = """SELECT * FROM "main"."web_search" """
            if search:
                query = """SELECT * FROM "main"."web_search" WHERE "criterion" LIKE '%{}%'""".format(search)
            cur.execute(query)
            # obtener todos los registros
            selection = cur.fetchall()
            if selection:
                history = []
                for web_search in selection:
                    criterion = web_search[2]
                    engine = get_engine_by_name(web_search[4])
                    request_type = get_request_type_by_name(web_search[5])
                    h = WebSearch("", "", criterion, engine, request_type, results=10)
                    h.creation_date = datetime.strptime(web_search[0], "%Y-%m-%d %H:%M:%S.%f")
                    h.FOUNDED = True if web_search[1] == "True" else False
                    h.criterion = web_search[2]
                    h.url = web_search[3]
                    h.path_attachment = web_search[6]
                    h.elapsed_time = web_search[7]
                    h.size = web_search[8]
                    #
                    history.append(h)
                return history
    except sqlite3.Error as e:
        print(e.args)
        SENT_TO_LOG(f"Obteniendo búsqueda de la DB {e.args}", "ERROR")

def GET_SEARCHES():
    try:
        with sqlite3.connect(DB_FILE) as con:
            cur = con.cursor()
            query = """SELECT "criterion" FROM "main"."web_search" """
            cur.execute(query)
            selection = cur.fetchall()
            if selection:
                selection_wo_duplicated = []
                for i in selection:
                    if i[0] not in selection_wo_duplicated:
                        selection_wo_duplicated.append(i[0])
                return selection_wo_duplicated
    except sqlite3.Error as e:
        print(e.args)
        SENT_TO_LOG(f"Obteniendo búsqueda de la DB {e.args}", "ERROR")
