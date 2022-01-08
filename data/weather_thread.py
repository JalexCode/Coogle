from PyQt5.QtCore import QObject, pyqtSignal

from data.weather import Weather

class WeatherRequestThread(QObject):
    send_request_signal = pyqtSignal(int, bool, str, str, str, bool)
    check_mailbox_signal = pyqtSignal(int, bool, str, str, str, bool)
    check_content_signal = pyqtSignal(int, bool, str, str, str, bool)
    error_signal = pyqtSignal(str, object)
    finish_signal = pyqtSignal(object)
    def __init__(self, user, passw, city, parent=None):
        QObject.__init__(self)
        #self.parent = parent
        self.user = user
        self.passw = passw
        self.city = city
        self.w = None

    def run(self):
        self.w = Weather(self.user, self.passw, self.city)
        if not self.w.FOUNDED:
            self.w.signals(self.send_request_signal, self.check_mailbox_signal, self.check_content_signal, self.error_signal, self.finish_signal)
            self.w.send_request()
            #
            self.w.fetch_msg()
            self.w.receive_data()