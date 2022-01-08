# >--------------------------------------- DATABASE ------------------------------------------------------------------<
# directorio de la base de datos
import base64
import os
import pickle
import random
import sqlite3

from util.const import APP_DATA
from util.logger import SENT_TO_LOG

DB_FILE = os.path.join(APP_DATA, "user_data.db")

def GET_CURRENT_USER():
    path = os.path.join(APP_DATA, "user.bin")
    if os.path.exists(path):
        with open(path, "rb") as current_user:
            user = pickle.load(current_user)
            pick_in_db = SELECT_ONE_USER(user)
            if pick_in_db is not None:
                return pick_in_db

def CREATE_DB():
    # si no existe la creo
    if not os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "w") as db:
                db.write("")
        except Exception as e:
            msg = f"No se pudo crear el archivo DB > {e.args}"
            SENT_TO_LOG(msg)
        # creo las tablas con sus columnas
        with sqlite3.connect(DB_FILE) as temp_conexion:
            temp_cursor = temp_conexion.cursor()
            #query_delete = """DROP TABLE IF EXISTS "main"."users";"""
            query_users = """CREATE TABLE "main"."users" (
            "user" text NOT NULL,
            "password" text,
            PRIMARY KEY ("user") ON CONFLICT IGNORE
            );"""
            #temp_cursor.execute(query_delete)
            temp_cursor.execute(query_users)
            # cerrar conexion y cursor
            temp_cursor.close()
            temp_conexion.commit()

#>----------------------------------- USUARIO --------------------------------------------------------------------
class Usuario:
    def __init__(self, mail, passw):
        self.mail = mail
        self.passw = passw

    def encode_passw(self):
        try:
            texto = self.passw
            abc = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
            abc_lower = abc.lower()
            # CAESAR
            # cantidad de desplazamiento
            n = random.randint(2, 8)
            # Variable para guardar mensaje cifrado
            cifrado = ""
            # Iteramos por cara letra del mensaje
            for l in texto:
                # Si la letra está en el abecedario se reemplaza
                if l in abc:
                    pos_letra = abc.index(l)
                    # Sumamos para movernos a la derecha del abc
                    nueva_pos = (pos_letra + n) % len(abc)
                    cifrado += abc[nueva_pos]
                elif l in abc_lower:
                    pos_letra = abc_lower.index(l)
                    # Sumamos para movernos a la derecha del abc
                    nueva_pos = (pos_letra + n) % len(abc)
                    cifrado += abc_lower[nueva_pos]
                else:
                    # Si no está en el abecedario sólo añadelo
                    cifrado += l
            caesar = f"{n}{cifrado}"
            base64_caesar_encoder = base64.encodebytes(caesar.encode("utf-8"))
            return base64_caesar_encoder.decode("utf-8")
        except Exception as e:
            SENT_TO_LOG(f"Codificando contraseña {e.args}", "ERROR")

    def decode_passw(self):
        try:
            texto = self.passw
            if type(texto) == str:
                texto = texto.encode("utf-8")
            abc = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
            abc_lower = abc.lower()
            #
            base64_caesar_encoded_passw = base64.decodebytes(texto)
            texto = base64_caesar_encoded_passw.decode("utf-8")
            i = int(texto[0])
            # Guardar posible mensaje
            descifrado = ""
            for l in texto:
                # Si la letra está en el abecedario reemplazamos
                if l in abc:
                    pos_letra = abc.index(l)
                    # Restamos para movernos a la izquierda
                    nueva_pos = (pos_letra - i) % len(abc)
                    descifrado += abc[nueva_pos]
                elif l in abc_lower:
                    pos_letra = abc_lower.index(l)
                    # Restamos para movernos a la izquierda
                    nueva_pos = (pos_letra - i) % len(abc)
                    descifrado += abc_lower[nueva_pos]
                else:
                    descifrado += l
            return descifrado[1:]
        except Exception as e:
            SENT_TO_LOG(f"Decodificando contraseña {e.args}", "ERROR")

    def __eq__(self, other):
        return self.mail == other.mail

    def __str__(self):
        return F"{self.mail} {self.passw}"

def SELECT_USERS():
    try:
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()
        query = """SELECT * FROM "main"."users"; """
        cur.execute(query)
        user = []
        selection = cur.fetchall()
        if selection:
            for usuario in selection:
                user.append(Usuario(*usuario))
        cur.close()
        con.close()
        return user
    except Exception as e:
        SENT_TO_LOG(f"Seleccionando usuarios de la DB {e.args}", "ERROR")
        print("Seleccionando usuarios de la DB")

def SELECT_ONE_USER(mail):
    try:
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()
        query = """SELECT * FROM "main"."users" WHERE "users"."user" = ?; """
        cur.execute(query, [mail,])
        selection = cur.fetchone()
        if selection:
            return Usuario(*selection)
        con.close()
    except Exception as e:
        SENT_TO_LOG(f"Seleccionando un usuario de la DB {e.args}", "ERROR")
        print(f"Seleccionando un usuario de la DB {e.args}")

#print(SELECT_USERS())
# agregar usuario
def ADD_USER(user):
    try:
        con = sqlite3.connect(DB_FILE)
        cur = con. cursor()
        query = """INSERT INTO "main"."users" ("user", "password") VALUES (?, ?);"""
        cur.execute(query, [user.mail, user.encode_passw()])
        con.commit()
        con.close()
    except sqlite3.Error as e:
        SENT_TO_LOG(f"Añadiendo usuario a la DB {e.args}", "ERROR")
        print(f"Añadiendo usuario a la DB {e.args}")

# actualizar contrasenna
def UPDATE_PASSW(user):
    try:
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()
        query = """UPDATE "main"."users" SET "password" = ? WHERE user= ?"""
        cur.execute(query, [user.passw, user.phone])
        con.commit()
        con.close()
    except sqlite3.Error as e:
        SENT_TO_LOG(f"Actualizando usuario en la DB {e.args}", "ERROR")
        print(f"Actualizando usuario en la DB {e.args}")
        #raise e

# eliminar usuario
def DEL_USER(user):
    try:
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()
        query = """DELETE FROM "main"."users" WHERE "user" = ?;"""
        cur.execute(query, [user.phone])
        con.commit()
        con.close()
    except sqlite3.Error as e:
        SENT_TO_LOG(f"Eliminando usuario de la DB {e.args}", "ERROR")
        print(f"Eliminando usuario de la DB {e.args}")
        #raise e
