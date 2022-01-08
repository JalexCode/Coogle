from PyQt5.QtCore import QObject, pyqtSignal

from data.translator import Translator

class TranslatorRequestThread(QObject):
    send_request_signal = pyqtSignal(int, bool, str, str, str, bool)
    check_mailbox_signal = pyqtSignal(int, bool, str, str, str, bool)
    check_content_signal = pyqtSignal(int, bool, str, str, str, bool)
    error_signal = pyqtSignal(int, str, object)
    finish_signal = pyqtSignal(object)

    def __init__(self, user, passw, text_to_translate, from_lang, to_lang, parent=None):
        QObject.__init__(self)
        # self.parent = parent
        self.user = user
        self.passw = passw
        self.text_to_translate = text_to_translate
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.t = None

    def run(self):
        self.t = Translator(self.user, self.passw, self.text_to_translate, self.from_lang,  self.to_lang)
        if not self.t.FOUNDED:
            self.t.signals(self.send_request_signal, self.check_mailbox_signal, self.check_content_signal,
                           self.error_signal, self.finish_signal)
            self.t.send_request()
            #
            self.t.fetch_msg()
            self.t.receive_data()
