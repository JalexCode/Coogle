from PyQt5.QtCore import QObject, pyqtSignal

from data.web_search import WebSearch
from util.settings import SETTINGS

class WebSearchRequestThread(QObject):
    i = -1
    send_request_signal = pyqtSignal(int, bool, str, str, str, bool)
    check_mailbox_signal = pyqtSignal(int, bool, str, str, str, bool)
    check_content_signal = pyqtSignal(int, bool, str, str, str, bool)
    error_signal = pyqtSignal(str, object)
    finish_signal = pyqtSignal(object)
    def __init__(self, web_search):
        QObject.__init__(self)
        #self.parent = parent
        self.w_s = web_search
        self.w_s.i = self.i
        #

    def run(self, only_receive=False):
        if not self.w_s.FOUNDED:
            self.w_s.signals(self.send_request_signal, self.check_mailbox_signal, self.check_content_signal,
                             self.error_signal, self.finish_signal)
            if not only_receive:
                self.w_s.send_request()
                #
            self.w_s.fetch_msg()
            self.w_s.receive_data()

    def set_i(self, value):
        self.i = value
        if self.w_s is not None:
            self.w_s.i = value