from hashlib import md5
import os

from bs4 import BeautifulSoup
from imap_tools import MailBoxUnencrypted

from util.const import APP_DATA, SearchEngine, RequestType, IMAP_HOST, IMAP_PORT, nz
from util.decompress import unzip_with_7zip
from util.logger import SHOW_CONSOLE_LOG, SENT_TO_LOG
from data.service import Service

class WebSearch(Service):
    def __init__(self, user: str, passw: str, criterion: str, engine=SearchEngine.GOOGLE, request_type=RequestType.HTML, results=10):
        Service.__init__(self, user, passw, criterion)
        self.engine = engine
        self.request_type = request_type
        self.results = results
        self._url = ""
        # setup Mime text
        self.setup_mime_text()
        # texto del correo
        self.html = ""
        # archivo_adjunto
        self.path_attachment = ""
        # encoded name
        self.md5_encoded_name = md5(f"{self.creation_date}{self.criterion}".encode("utf-8")).hexdigest()
        # elapsed time
        self.elapsed_time = "00:00:00"

    def setup_subject(self):
        if not self._url:
            is_url, criterion = self.encoding_criterion(True)
            if not is_url:
                SHOW_CONSOLE_LOG("2.0.2", "Construyendo URL con Motor de busqueda", 2)
                if self.engine == SearchEngine.GOOGLE or self.engine == SearchEngine.BING:
                    criterion = self.engine.value.format(criterion, self.results)
                elif self.engine == SearchEngine.GOOGLE_IMG or self.engine == SearchEngine.WIKIPEDIA:
                    criterion = self.engine.value.format(criterion)
            else:
                if "wikipedia" in criterion:
                    self.engine = SearchEngine.WIKIPEDIA
                elif "bing" in criterion:
                    self.engine = SearchEngine.BING
            self._url = criterion
            # Asunto del mensaje
            subject = f"{self.request_type.value} {criterion}"
        else:
            # Asunto del mensaje
            subject = f"{self.request_type.value} {self._url}"
        self._message['Subject'] = subject
        SHOW_CONSOLE_LOG("INFO", f"Asunto creado!", 2)
        SHOW_CONSOLE_LOG("INFO", f"Cuerpo del mensaje:", 2)
        print(self._message)

    def receive_data(self):
        try:
            with MailBoxUnencrypted(IMAP_HOST, IMAP_PORT).login(self._user, self._passw) as imap:
                SHOW_CONSOLE_LOG("INFO", "Pagina Web", 1)
                MailMessage = Service.receive_data(self)
                if MailMessage:
                    # cache path
                    path = os.path.join(APP_DATA, "cache", self.md5_encoded_name)
                    try:
                        os.mkdir(path)
                    except:
                        pass
                    #
                    if self.request_type == RequestType.FULL_HTML or self.request_type == RequestType.PDF or \
                            self.engine == SearchEngine.GOOGLE_IMG:
                        SHOW_CONSOLE_LOG("5.1.1", "Descargando archivo adjunto...", 1)
                        # signal
                        self.check_content_signal.emit(self.i, True, "Descargando datos",
                                                       f"Descomprimiendo respuesta...",
                                                       ":/icons/icons/about.png", False)
                        # descargando los Adjuntos
                        attachments = MailMessage.attachments
                        for att in attachments:
                            filename, filetype = att.filename, att.content_type
                            file_path = os.path.join(path, filename)
                            with open(file_path, 'wb') as f:
                                f.write(att.payload)
                            if "zip" in filetype.lower():
                                unziped_filename, webpage_name = unzip_with_7zip(file_path, path)
                                if unziped_filename:
                                    self.path_attachment = os.path.join(path, webpage_name)
                                else:
                                    raise Exception("No se pudo descomprimir el archivo de respuesta")
                            elif "pdf" in filetype.lower():
                                self.path_attachment = os.path.join(path, "webpage.pdf")
                    elif self.request_type == RequestType.HTML or self.request_type == RequestType.TEXT:
                        SHOW_CONSOLE_LOG("5.1.1", "Descargando texto...", 1)
                        # coger contenido
                        self.html = MailMessage.text
                        # cache
                        file_path = os.path.join(path, "simple_webpage")
                        with open(file_path, 'w', encoding="utf-8") as f:
                            soup = BeautifulSoup(MailMessage.text, "html.parser")
                            f.write(soup.decode_contents())
                    #
                    self.check_content_signal.emit(self.i, True, "Hecho!",
                                                   f"Tamaño de la respuesta: {nz(self._size)}", ":/icons/icons/success_green.png",
                                                   False)
                    #
                    self.finish_signal.emit(self)
                    SHOW_CONSOLE_LOG("INFO", "ARCHIVO DESCARGADO!", 2)
                    #
                    SHOW_CONSOLE_LOG("5.1.2", "Eliminando el mensaje del servidor", 1)
                    imap.delete(MailMessage.uid)
                    SHOW_CONSOLE_LOG("INFO", "Archivo eliminado!", 2)
                    #
                    SHOW_CONSOLE_LOG("INFO", "Cerrando sesion", 1)
        except Exception as e:
            SENT_TO_LOG(f"Recibiendo texto del correo{e.args}")
            SHOW_CONSOLE_LOG("Error", f"Recibiendo texto del correo{e.args}")
            self.error_signal.emit("Recibiendo texto del correo", e.args)

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        self._url = value