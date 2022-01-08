from imap_tools import MailBoxUnencrypted

from util.const import TRANSLATOR, IMAP_HOST, IMAP_PORT, LANGUAGES
from util.logger import SHOW_CONSOLE_LOG, SENT_TO_LOG
from data.service import Service

class Translator(Service):
    # max caracteres
    MAX = 900
    def __init__(self, user: str, passw: str, criterion: str, _from:str="en", _to:str="es"):
        Service.__init__(self, user, passw, criterion)
        # prefijo de idiomas
        self.from_ = _from
        self.to_ = _to
        # setup Mime text
        self.setup_mime_text()
        # traduccion
        self.translation = ""

    def setup_subject(self):
        criterion = self.encoding_criterion(True)[1]
        SHOW_CONSOLE_LOG("2.0.2", "Construyendo URL para Google Translator", 2)
        criterion = TRANSLATOR.format(self.from_[0], self.to_[0], criterion)
        print(criterion)
        # Asunto del mensaje
        subject = f"source {criterion}"
        self._message['Subject'] = subject
        SHOW_CONSOLE_LOG("INFO", f"Asunto creado!", 2)
        SHOW_CONSOLE_LOG("INFO", f"Cuerpo del mensaje:", 2)
        print(self._message)

    def receive_data(self):
        try:
            with MailBoxUnencrypted(IMAP_HOST, IMAP_PORT).login(self._user, self._passw) as imap_server:
                SHOW_CONSOLE_LOG("INFO", "Pagina Web", 1)
                MailMessage = Service.receive_data(self)
                if MailMessage:
                    SHOW_CONSOLE_LOG("5.1.1", "Descargando texto...", 1)
                    # coger contenido
                    #io.StringIO(MailMessage.text)
                    unparsed = MailMessage.text
                    SHOW_CONSOLE_LOG("INFO", "TEXTO DESCARGADO!", 2)
                    #
                    SHOW_CONSOLE_LOG("5.1.2", "Eliminando el mensaje del servidor", 1)
                    imap_server.delete(MailMessage.uid)
                    SHOW_CONSOLE_LOG("INFO", "Archivo eliminado!", 2)
                    #
                    SHOW_CONSOLE_LOG("INFO", "Cerrando sesion", 1)
                    #
                    self.parse_response(unparsed)
        except Exception as e:
            SENT_TO_LOG(f"Recibiendo archivo WEB{e.args}")
            SHOW_CONSOLE_LOG("Error", f"Recibiendo archivo WEB{e.args}")

    def parse_response(self, unparsed:str):
        if unparsed:
            SHOW_CONSOLE_LOG("5.2", "Parseando respuesta")
            import json
            json_array = json.loads(unparsed.replace('\r\n', ''), strict=False)
            # extraigo cada linea traducida (las lineas se separaon por \n )
            translation = ""
            for translated_line in json_array[0]:
                # for c in range(2):
                translation += translated_line[0]
            # si el idioma era automatico
            if self.from_[0] == "auto":
                detected = json_array[2]
                for lang in LANGUAGES:
                    if lang[0] == detected:
                        self.from_ = lang
                        break
            self.translation = translation.strip()
            self.finish_signal.emit(self)
