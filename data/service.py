import datetime
import smtplib
import time
from email.mime.text import MIMEText

from imap_tools import MailBoxUnencrypted, AND
from urllib3.util import url

from util.const import SMTP_HOST, SMTP_PORT, RUMKIN, IMAP_HOST, IMAP_PORT, nz
from util.logger import SENT_TO_LOG, SHOW_CONSOLE_LOG
from util.returnable_thread import ThreadWithReturnValue

RETRY = 5

class Service:
    def __init__(self, user: str, passw: str, criterion: str):
        # credenciales
        self._user = user
        self._passw = passw
        # criterion
        self.criterion = criterion
        # Mime text
        self._message = None
        # URL
        self._url = ""
        # tiempo de espera
        self._wait_time = 30
        # size
        self._size = 0
        # fecha creado
        self.creation_date = datetime.datetime.now()
        # fecha enviado
        self.sended_date = datetime.datetime.now()
        # fecha responido
        self.answered_date = datetime.datetime.now()
        # fecha recibido
        self.received_date = datetime.datetime.now()
        # uid
        self._uid = None
        # msg-object
        self._msg_object = None
        # FLAGS
        # indica si el mensaje fue encontrado o no
        self.FOUNDED = False
        # indica si el mensaje fue descargado o no
        self._DOWNLOADED = False
        # idx
        self.__i = -1

    @property
    def i(self):
        return self.__i

    @i.setter
    def i(self, value):
        self.__i = value

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        self._user = value

    @property
    def passw(self):
        return self._passw

    @passw.setter
    def passw(self, value):
        self._passw = value

    def signals(self, send_request, check_mailbox, check_content, error, finish):
        self.send_request_signal = send_request
        self.check_mailbox_signal = check_mailbox
        self.check_content_signal = check_content
        self.error_signal = error
        self.finish_signal = finish

    def setup_mime_text(self):
        SHOW_CONSOLE_LOG("2.0", "* Creando cuerpo de peticion *")
        self._message = MIMEText("")
        self._message['From'] = self._user
        self._message['To'] = RUMKIN
        self.setup_subject()

    def setup_subject(self):
        SHOW_CONSOLE_LOG("2.1", "Creando asunto", 1)
        # Asunto del mensaje
        self._message['Subject'] = f"send lista"

    def send_request(self):
        for i in range(RETRY):
            try:
                # iniciar SMTP
                SHOW_CONSOLE_LOG("1.0", "* Iniciando servidor SMTP *")
                with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=5) as smtp_server:
                    smtp_server.login(self._user, self._passw)
                    try:
                        # Mime text
                        self.setup_mime_text()
                        # Enviando correo
                        SHOW_CONSOLE_LOG("3.0", "* Enviando peticion *")
                        #
                        t0 = time.time()
                        smtp_server.sendmail(self._user, RUMKIN, self._message.as_string())
                        self.sended = datetime.datetime.now()
                        #
                        SHOW_CONSOLE_LOG("INFO", "Solicitud enviada!", 1)
                        SHOW_CONSOLE_LOG("INFO", "Cerrando sesion", 1)
                        # signal
                        self.send_request_signal.emit(self.i, True, "Solicitud enviada!", f"Enviado satisfactoriamente en {round(time.time() - t0, 2)} segundos", ":/icons/icons/send.png", True)
                    except smtplib.SMTPResponseException as e:
                        SENT_TO_LOG(f"No se pudo enviar la solicitud {e.args}")
                        SHOW_CONSOLE_LOG("Error", f"No se pudo enviar la solicitud {e.args}")
                        # signal
                        self.send_request_signal.emit(self.i, False, f"No se pudo enviar la solicitud", "Al parecer ha ocurrido un error de SMTP", ":/icons/icons/warning_QR.png", True)  # {e.args}")
            except Exception as e:
                SENT_TO_LOG(f"No se pudo enviar la solicitud {e.args}")
                SHOW_CONSOLE_LOG("Error",f"Revise su conexión a Internet {e.args}")
                self.send_request_signal.emit(self.i, False, "Solicitud cancelada", f"Revise su conexión a Internet", ":/icons/icons/critical.png", True)
            else:
                break
            if i == RETRY-1:
                self.send_request_signal.emit(self.i, False, "Solicitud cancelada", f"Máximo de intentos alcanzados. Revise su conexión a Internet", ":/icons/icons/critical.png", True)

    def criterion_is_url(self):
        return self.criterion.startswith("https://") or self.criterion.startswith("http://")

    def encoding_criterion(self, is_url=True):
        txt = self.criterion
        #try:
        SHOW_CONSOLE_LOG("2.0.1", "Creando asunto", 2)
        # si es una URL no hace nada
        if self.criterion_is_url():
            SHOW_CONSOLE_LOG("INFO", "El criterio de busqueda es una URL", 2)
            return True, txt
        # si es una frase, la codifica
        SHOW_CONSOLE_LOG("INFO", "Codificando URL", 2)
        # charset para codificacion
        CHARSET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        if is_url:
            # si es un criterio de busqueda WEB le agrega los +
            txt = txt.split()
            for i in range(len(txt)):
                txt[i] = url._encode_invalid_chars(txt[i], CHARSET)
            txt = "+".join(txt)
        else:
            # si no es para busqueda, solo retorno la url normal codificada
            txt = url._encode_invalid_chars(txt, CHARSET)
        SHOW_CONSOLE_LOG("INFO", f"URL codificada! > {txt}", 2)
        return False, txt
        #except Exception as e:
        #    SENT_TO_LOG(f"Codificando URL {str(e.args)}")
        #    SHOW_CONSOLE_LOG("Error", f"Codificando URL {str(e.args)}")

    def check_mailbox(self, check=False):
        try:
            with MailBoxUnencrypted(IMAP_HOST, IMAP_PORT).login(self._user, self._passw) as imap_server:
                try:
                    SHOW_CONSOLE_LOG("4.1.1", "Chequeando mailbox", 1)
                    #
                    nums = []
                    retries = 0
                    while not nums:
                        nums = imap_server.search("FROM webpage@rumkin.com ALL")
                        if nums:
                            nums = nums[0]
                            plural = 's' if len(nums.split()) > 1 else ''
                            SHOW_CONSOLE_LOG("INFO", f"Encontrado {len(nums.split())}", 2)
                            if nums:
                                # signal
                                self.check_mailbox_signal.emit(self.i, True, f"Respuesta{plural} encontrada{plural}", f"Encontrada{plural} {len(nums.split())} respuesta{plural}",":/icons/icons/about.png",False)
                                break
                        if check:
                            return nums
                        # cada 30 segundos repito la operacion
                        SHOW_CONSOLE_LOG("INFO", f"No se encontro nada! Esperando {self._wait_time} segundos", 2)
                        # signal
                        self.check_mailbox_signal.emit(self.i, False, "No se encontró respuesta. Por favor, espere", f"No se encontró nada! Esperando {self._wait_time} segundos", ":/icons/icons/warning_QR.png", False)
                        # time
                        time.sleep(self._wait_time)
                        #
                        if retries == RETRY:
                            raise Exception("Máximo de intentos alcanzados")
                        retries += 1
                    return nums
                except Exception as e:
                    SENT_TO_LOG(f"Inspeccionando bandeja de entrada {e.args}")
                    SHOW_CONSOLE_LOG("Error", f"Inspeccionando bandeja de entrada {e.args}")
        except Exception as e:
            if e.args[0] == 10051:
                self.check_mailbox_signal.emit(self.i, False, "Revise su conexión a Internet",
                                               "No se pudo iniciar el servidor IMAP4", ":/icons/icons/critical.png", True)
            SENT_TO_LOG(f"No se pudo iniciar el servidor IMAP4 {e.args}")
            SHOW_CONSOLE_LOG("Error", f"No se pudo iniciar el servidor IMAP4 {e.args}")

    def check_content(self):
        try:
            while not self.FOUNDED:
                with MailBoxUnencrypted(IMAP_HOST, IMAP_PORT).login(self._user, self._passw) as imap_server:
                    SHOW_CONSOLE_LOG("4.1.2", f"Comprobando Asunto", 1)
                    try:
                        for MailMessage in imap_server.fetch(AND(subject="Re: " + self._message["Subject"])):#(content_type="application/zip")):#text=
                            #
                            #print(parse_email_addresses(MailMessage.headers))
                            # uid
                            self._uid = MailMessage.uid #content_id
                            # asunto
                            subject = MailMessage.subject
                            SHOW_CONSOLE_LOG("INFO", f"URL ENCONTRADA! ({subject})", 2)
                            # tamanno
                            size = MailMessage.size_rfc822
                            self._size = size
                            SHOW_CONSOLE_LOG("INFO", f"Tamaño en bytes: {self._size}", 2)
                            # msg_id
                            # self._msg_id = MailMessage.headers["message-id"]
                            # actualizo flag encontrado
                            self.FOUNDED = True
                            # signal
                            self.check_content_signal.emit(self.i, True, "Datos recibidos", f"Tamaño de la respuesta: {nz(self._size)}", ":/icons/icons/about.png", False)
                            # set msg object
                            self._msg_object = MailMessage
                            break
                    except:
                        pass
                    if self.FOUNDED:
                        break
                    # signal
                    self.check_content_signal.emit(self.i, False, "La respuesta no era la esperada", "No se encontró. Buscando respuesta...", ":/icons/icons/warning_QR.png", False)
                    # sleep
                    time.sleep(self._wait_time)
        except Exception as e:
            SENT_TO_LOG(f"No se pudo iniciar el servidor IMAP4 {e.args}")
            SHOW_CONSOLE_LOG("Error", f"No se pudo iniciar el servidor IMAP4 {e.args}")
            self.check_content_signal.emit(self.i, False, "Revise su conexión a Internet", "No se pudo iniciar el servidor IMAP4", ":/icons/icons/critical.png", True)

    def fetch_msg(self):
        try:
            # reviso que el mensaje entre en la bandeja de entrada
            SHOW_CONSOLE_LOG("4.1", "* Preparando para recibir datos *")
            # inicio el hilo para chequear mensajes de rumkin
            thread_mailbox = ThreadWithReturnValue(target=self.check_mailbox)
            thread_mailbox.start()
            nums = thread_mailbox.join()
            # inicio el hilo para chequear el mensaje que espero
            thread_msg_id = ThreadWithReturnValue(target=self.check_content)
            thread_msg_id.start()
            thread_msg_id.join()
            if self.FOUNDED:
                SHOW_CONSOLE_LOG("INFO", f"Listo para la descarga!", 2)
        except Exception as e:
            SENT_TO_LOG(f"No se encontro el correo de respuesta {e.args}")
            SHOW_CONSOLE_LOG("Error", f"No se encontro el correo de respuesta {e.args}")

    def receive_data(self):
        # receive data
        SHOW_CONSOLE_LOG("5.0", "* Recibir datos *")
        #
        #SHOW_CONSOLE_LOG("5.0.1", f"Seleccionando mensaje por UID {self._uid}", 1)
        #with MailBoxUnencrypted(IMAP_HOST, IMAP_PORT).login(self._user, self._passw) as imap_server:
        #    for MailMessage in imap_server.fetch(AND(uid=self._uid)):
        return self._msg_object

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value