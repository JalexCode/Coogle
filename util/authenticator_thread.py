from PyQt5.QtCore import QObject, pyqtSignal

from util.authentificator import Authenticator

class AuthenticatorThread(QObject):
    send_key_signal = pyqtSignal(bool, str)
    error_signal = pyqtSignal(str, str)
    def __init__(self, user, passw):
        QObject.__init__(self)
        self.user = user
        self.passw = passw
        #
        self.authentificator = None

    def run(self):
        self.authentificator = Authenticator(self.user, self.passw)
        self.authentificator.signals(self.send_key_signal, self.error_signal)
        self.authentificator.send_key()

    def check_key(self, key):
        return self.authentificator.check_key(key)