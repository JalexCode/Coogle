import re
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog, QMessageBox, QInputDialog

from ui.settings import Ui_Dialog
from util.authenticator_thread import AuthenticatorThread
from util.database_handler import SELECT_USERS, GET_CURRENT_USER, SELECT_ONE_USER, ADD_USER, Usuario
from util.logger import SENT_TO_LOG
from util.settings import SETTINGS, SAVE_SETTINGS, DEFAULT_SETTINGS

class Preferences(Ui_Dialog, QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self)
        # loading ui file
        #uic.loadUi("ui/settings.ui", self)
        self.setupUi(self)
        # parent
        self.parent = parent
        # vars
        self.authentificator_in_progress = False
        self.authenticated = False
        # connections
        self.connections()
        # load configuration
        self.load_settings()

    def connections(self):
        self.authenticate.clicked.connect(self.authenticate_user)
        self.save.clicked.connect(self.save_settings)
        self.reset_to_default.clicked.connect(self.to_default)

    def to_default(self):
        try:
            for setting in DEFAULT_SETTINGS:
                SAVE_SETTINGS(setting, DEFAULT_SETTINGS[setting])
            self.load_settings()
        except Exception as e:
            self.error("Restaurando configuraciones", e.args)

    def load_settings(self):
        try:
            self.load_user()
            self.set_auth_status(self.authenticated)
            # > -------------------------------------------------------------- < #
            frequency = SETTINGS.value("check_mailbox")
            if frequency == "auto":
                self.frequency.setCurrentIndex(1)
            elif frequency == "manual":
                self.frequency.setCurrentIndex(2)
            if frequency == "both":
                self.frequency.setCurrentIndex(0)
            # > -------------------------------------------------------------- < #
            save_cache = SETTINGS.value("save_cache", type=bool)
            self.save_cache.setChecked(save_cache)
            # > -------------------------------------------------------------- < #
            sound_path = SETTINGS.value("alert_sound")
            self.sound_path.setText(sound_path)
            # > -------------------------------------------------------------- < #
            show_systray_icon = SETTINGS.value("show_systray_icon", type=bool)
            self.show_systray_icon.setChecked(show_systray_icon)
            # > -------------------------------------------------------------- < #
        except Exception as e:
            self.error("Cargando preferencias", e.args)

    def save_settings(self):
        try:
            # > -------------------------------------------------------------- < #
            frequency = SETTINGS.value("check_mailbox")
            if frequency == "auto":
                self.frequency.setCurrentIndex(1)
            elif frequency == "manual":
                self.frequency.setCurrentIndex(2)
            if frequency == "both":
                self.frequency.setCurrentIndex(0)
            # > -------------------------------------------------------------- < #
            save_cache = SETTINGS.value("save_cache", type=bool)
            self.save_cache.setChecked(save_cache)
            # > -------------------------------------------------------------- < #
            sound_path = SETTINGS.value("alert_sound")
            self.sound_path.setText(sound_path)
            # > -------------------------------------------------------------- < #
            show_systray_icon = SETTINGS.value("show_systray_icon", type=bool)
            self.show_systray_icon.setChecked(show_systray_icon)
            # > -------------------------------------------------------------- < #
        except Exception as e:
            self.error("Guardando preferencias", e.args)

    def load_user(self):
        try:
            user = SETTINGS.value("current_user", type=str)
            passw = ""
            if user:
                user_from_bd = SELECT_ONE_USER(user)
                passw = user_from_bd.decode_passw()
                #
                self.authenticated = True
                #
                self.mail.setText(user)
                self.password.setText(passw)
            else:
                self.authenticated = False
            self.mail.setText(user)
            self.password.setText(passw)
        except Exception as e:
            self.error("Obteniendo datos del usuario", e.args)

# > ----------------------------- AUTHENTICATION ------------------------------------------------------------< #
    def validating_credentials(self):
        mail = self.mail.text()
        passw = self.password.text()
        if mail and passw:
            if re.search("^[a-zA-Z0-9\._-]+@[a-zA-Z0-9-]{2,}[.][a-zA-Z]{2,4}$", mail, re.I):
                return mail, passw

    def authenticate_user(self):
        try:
            credentials = self.validating_credentials()
            if credentials is not None:
                mail, passw = credentials
                # mail thread
                authentificator = AuthenticatorThread(mail, passw)
                authentificator.error_signal.connect(self.error)
                authentificator.send_key_signal.connect(self.set_status)
                authentificator.run()
                # set un-authenticated
                self.authenticated = False
                self.authentificator_in_progress = True
                while True:
                    auth_code, ok = QInputDialog.getText(self, "Autenticación de usuario",
                                                             "Introduzca el código de autenticación")
                    if ok:
                        auth_code = auth_code.strip()
                        if "-" in auth_code:
                            splited = auth_code.split("-")
                            if len(splited) == 8:
                                joined = "".join(splited)
                                if len(joined) == 32:
                                    raw_code = auth_code.replace("-", "").lower()
                                    if authentificator.check_key(raw_code):
                                        self.set_authenticated(True)
                                        break
                        else:
                            self.set_status(False, "Código incorrecto")
                    else:
                        self.set_status(False, "Autenticación cancelada. Usuario sin autenticación.")
                        self.set_auth_status(False)
                        break
        except Exception as e:
            self.error("Error durante el proceso de autenticación", e.args)

    def set_authenticated(self, indicator):
        self.set_status(True, "Usuario autenticado!")
        self.set_auth_status(True)
        self.authenticated = True
        self.authentificator_in_progress = False
        # add to db
        mail, passw = self.mail.text().strip(), self.password.text()
        user = Usuario(mail, passw)
        ADD_USER(user)
        # save setting
        SAVE_SETTINGS("current_user", mail)

    def set_status(self, indicator, txt):
        self.status_txt.setText(txt)
        self.set_status_icon(indicator)

    def set_auth_status(self, indicator):
        if indicator:
            self.auth_status.setToolTip('Está autenticado')
            self.auth_status.setPixmap(QPixmap(":/icons/icons/success_op.png"))
        else:
            self.auth_status.setPixmap(QPixmap(":/icons/icons/bad.png"))
            self.auth_status.setToolTip('No está autenticado')

    def set_status_icon(self, indicator):
        if indicator:
            self.status_icon.setPixmap(QPixmap(":/icons/icons/success_green.png"))
        else:
            self.status_icon.setPixmap(QPixmap(":/icons/icons/warning_QR.png"))

    def freeze_ui(self, freeze):
        self.mail.setEnabled(freeze)
        self.password.setEnabled(freeze)
        self.authenticate.setEnabled(freeze)
        self.save.setEnabled(freeze)

    def closeEvent(self, event):
        if not self.authentificator_in_progress:
            event.accept()

    def error(self, place, text):
        # logs
        SENT_TO_LOG(text)
        # status
        self.set_status_icon(":/icons/icons/critical.png")
        self.status_txt.setText("Error!")
        # error message
        msg = QMessageBox()
        # msg.setStyleSheet(DARK_STYLE)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Error")
        msg.setText("Ha ocurrido un error!")
        msg.setInformativeText(f"-> {place}")
        msg.setDetailedText(str(text))
        msg.exec_()
