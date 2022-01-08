import datetime
import smtplib
import time
from email.mime.text import MIMEText

from hashlib import md5

from util.const import SMTP_HOST, SMTP_PORT
from util.logger import SENT_TO_LOG, SHOW_CONSOLE_LOG

FROM = "YOUR_ACCOUNT", "YOUR_PASSWORD"

class Authenticator:
    def __init__(self, user: str, passw: str):
        # credenciales
        self._user = user
        self._passw = passw
        # autenticado
        self._athenticated = False
        # auth key
        self._key = md5(f"{datetime.datetime.now()}{chr(0)}{self._user}{chr(0)}{self._passw}".encode("utf-8")).hexdigest()
        print(self._key)
        # message to send
        self._message = None

    def check_key(self, key):
        return self._key == key

    def signals(self, send_key, error):
        self.send_key_signal = send_key
        self.error_signal = error

    def setup_mime_text(self):
        SHOW_CONSOLE_LOG("2.0", "* Creando cuerpo de peticion *")
        self._message = MIMEText("")
        self._message['From'] = "javierglez99@nauta.cu"
        self._message['To'] = self._user
        SHOW_CONSOLE_LOG("2.1", "Creando asunto", 1)
        self._message['Subject'] = "Coogle Authorization Key"
        # creating code key
        code = ""
        for i in range(0, len(self._key), 4):
            code += self._key[i:i + 4].upper() + "-"
        code = code.strip().strip("-")
        #
        self._message["Text"] = "Codigo de autenticacion de Coogle: %s\nIntroduzca este codigo en la ventana del programa que lo solicita. Si no llena este campo, no podra usar Coogle con el correo %s"%(code, self._user)
        print(self._message)

    def send_key(self):
        for i in range(5):
            try:
                # iniciar SMTP
                SHOW_CONSOLE_LOG("1.0", "* Iniciando servidor SMTP *")
                with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=5) as smtp_server:
                    smtp_server.login(*FROM)
                    try:
                        # Mime text
                        self.setup_mime_text()
                        # Enviando correo
                        SHOW_CONSOLE_LOG("3.0", "* Enviando AUTH KEY *")
                        #
                        t0 = time.time()
                        smtp_server.sendmail(FROM[0], self._user, self._message.as_string())
                        self.sended = datetime.datetime.now()
                        #
                        SHOW_CONSOLE_LOG("INFO", "AUTH KEY enviada!", 1)
                        SHOW_CONSOLE_LOG("INFO", "Cerrando sesion", 1)
                        # signal
                        self.send_key_signal.emit(True, "Clave enviada")
                    except smtplib.SMTPResponseException as e:
                        SENT_TO_LOG(f"No se pudo enviar la solicitud {e.args}")
                        SHOW_CONSOLE_LOG("Error", f"No se pudo enviar la solicitud {e.args}")
                        # signal
                        self.error_signal.emit(f"No se pudo enviar la clave", "Posibles causas:\n- No se pudo iniciar la conexión con SMTP. Revise su conexión a Internet")
            except Exception as e:
                SENT_TO_LOG(f"Intento {i+1}. No se pudo enviar la solicitud {e.args}")
                SHOW_CONSOLE_LOG("Error",f"Intento {i+1}. Revise su conexión a Internet {e.args}")
                self.error_signal.emit(f"Intento {i+1}. Envío de clave cancelado", "Posibles causas:\n- No se pudo iniciar la conexión con SMTP. Revise su conexión a Internet\n- Credenciales incorrectas")
            else:
                break

# TESTING
#a = Authenticator("franklorenzo@nauta.cu", "frankito65")
#a.send_key()
#a.fetch_msg()
