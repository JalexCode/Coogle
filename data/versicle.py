from bs4 import BeautifulSoup
from imap_tools import MailBoxUnencrypted

from util.const import IMAP_HOST, IMAP_PORT, TranslateType, VersicleType
from util.logger import SHOW_CONSOLE_LOG, SENT_TO_LOG
from data.service import Service

class Versicle(Service):
    def __init__(self, user: str, passw: str, criterion: str, type:VersicleType=VersicleType.DAILY, translate_to:TranslateType=TranslateType.VALERA1960.value):
        Service.__init__(self, user, passw, criterion)
        # tipo
        self.type = type
        # traduccion
        self.translate_to = translate_to
        # setup Mime text
        self.setup_mime_text()
        # text
        self.text = ""
        # verse
        self.verse= ""

    def setup_subject(self):
        print(self.type)
        print(self.translate_to)
        SHOW_CONSOLE_LOG("2.1", "Creando asunto", 1)
        criterion = ""
        if self.type == VersicleType.RANDOM:
            import random
            random = random.randint(0, 1301)
            criterion = self.type.value.format(self.translate_to, random)
        else:
            criterion = self.type.value.format(self.translate_to)
        # Asunto del mensaje
        subject = f"source {criterion}"
        self._message['Subject'] = subject
        SHOW_CONSOLE_LOG("INFO", f"Asunto creado!", 2)
        SHOW_CONSOLE_LOG("INFO", f"Cuerpo del mensaje:", 2)
        print(self._message)

    def receive_data(self):
        try:
            with MailBoxUnencrypted(IMAP_HOST, IMAP_PORT).login(self._user, self._passw) as imap:
                SHOW_CONSOLE_LOG("INFO", "Versículo en HTML", 1)
                MailMessage = Service.receive_data(self)
                if MailMessage:
                    SHOW_CONSOLE_LOG("5.1.1", "Descargando texto...", 1)
                    # coger contenido
                    #io.StringIO(MailMessage.text)
                    unparsed = MailMessage.text
                    SHOW_CONSOLE_LOG("INFO", "TEXTO DESCARGADO!", 2)
                    #
                    SHOW_CONSOLE_LOG("5.1.2", "Eliminando el mensaje del servidor", 1)
                    imap.delete(MailMessage.uid)
                    SHOW_CONSOLE_LOG("INFO", "Archivo eliminado!", 2)
                    #
                    SHOW_CONSOLE_LOG("INFO", "Cerrando sesion", 1)
                    #
                    self.parse_response(unparsed)
        except Exception as e:
            SENT_TO_LOG(f"Recibiendo texto del correo{e.args}")
            SHOW_CONSOLE_LOG("Error", f"Recibiendo texto del correo{e.args}")

    def parse_response(self, unparsed:str):
        if unparsed:
            SHOW_CONSOLE_LOG("5.2", "Parseando respuesta")
            # parseando
            try:
                html = BeautifulSoup(unparsed, "html.parser")
                text = html.find("div", {"class": "dailyVerses bibleText"})
                self.text = text.text
                verse = html.find("div", {"class": "dailyVerses bibleVerse"})
                self.verse = verse.text
                print(text.text)
                print(verse.text)
            except Exception as e:
                print(e.args)
            # signal
            self.finish_signal.emit(self)
