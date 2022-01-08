from PyQt5.QtCore import QObject, pyqtSignal

from data.versicle import Versicle
from util.const import TranslateType, VersicleType
from util.settings import SETTINGS


class VersicleRequestThread(QObject):
    send_request_signal = pyqtSignal(int, bool, str, str, str, bool)
    check_mailbox_signal = pyqtSignal(int, bool, str, str, str, bool)
    check_content_signal = pyqtSignal(int, bool, str, str, str, bool)
    error_signal = pyqtSignal(int, str, object)
    finish_signal = pyqtSignal(object)

    def __init__(self, user, passw, type, translate_to, parent=None):
        QObject.__init__(self)
        # self.parent = parent
        self.user = user
        self.passw = passw
        self.type = type
        self.translate_to = translate_to
        self.v = None

    def run(self):
        self.v = Versicle(self.user, self.passw, "", self.type, self.translate_to)
        if not self.v.FOUNDED:
            self.v.signals(self.send_request_signal, self.check_mailbox_signal, self.check_content_signal,
                           self.error_signal, self.finish_signal)
            self.v.send_request()
            #
            self.v.fetch_msg()
            self.v.receive_data()
