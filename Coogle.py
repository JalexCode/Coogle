from sys import argv

from PyQt5.QtCore import QSize, QTimer, QTime, QPoint, QDir, Qt
from PyQt5.QtGui import QPixmap, QFont, QPalette, QBrush, QIcon, QClipboard, QTextCursor
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QLabel, QMenu, QSystemTrayIcon, QFileDialog, \
    QAction, QInputDialog, QCompleter, QGraphicsDropShadowEffect, QSplashScreen

import threading

from data.translator import Translator
from data.translator_thread import TranslatorRequestThread
from data.versicle import Versicle
from data.versicle_thread import VersicleRequestThread
from data.weather import Weather
from data.weather_thread import WeatherRequestThread
from data.web_search import WebSearch
from data.web_search_thread import WebSearchRequestThread
from ui.animations import SeqAnimatedLabel, AnimType
from ui.changes_log import ChangesLOG
from ui.history import History
from ui.main import Ui_MainWindow
from ui.preferences import Preferences
from ui.web_search_page import WebSearchPage
from util.cache_db import CREATE_TABLES, INSERT_WEATHER, INSERT_VERSICLE, INSERT_TRANSLATION, INSERT_WEB_SEARCH, \
    GET_SEARCHES, UPDATE_WEB_SEARCH
from util.const import *
from util.database_handler import CREATE_DB, SELECT_ONE_USER
from util.logger import SENT_TO_LOG
from util.settings import SETTINGS, SAVE_SETTINGS
from util.sound import play_audio

class Coogle(Ui_MainWindow, QMainWindow):
    # CREAR BD
    CREATE_DB()
    # VERSICLES
    versicles_requests = []
    # TRANSLATIONS
    translation_requests = []
    # WEATHER
    weather_requests = []
    # WEB SEARCH
    web_search_requests = ["main"]
    # weather
    clouds_layer = LayerType.CLOUDY

    def __init__(self):
        QMainWindow.__init__(self)
        #
        #uic.loadUi("ui/main.ui", self)
        self.splash = QSplashScreen(QPixmap(':/logo/splash.png'))
        self.splash.show()
        #
        self.setupUi(self)
        #
        CREATE_TABLES()
        # elementos generados por codigo
        self.new_elements()
        # versiculos
        self.show_versicle_elements(False)
        # traductor
        self.fill_languages()
        # clima
        self.show_weather_elements(False)
        self.fill_municip()
        # web
        self.web_search_request_type.setCurrentIndex(2)
        self.web_search_tab.tabCloseRequested.connect(self.close_tab)
        # autocompletamiento
        self.set_web_search_completer()
        # conecciones
        self.connections()
        # cargar_estilos
        self.load_styles()
        # efectos
        self.load_effects()
        # cargar ultimos datos
        self.load_last_data()
        # icon tray
        self.system_tray_icon = QSystemTrayIcon(QIcon(":logo/logo.png"))
        self.menu = QMenu(self)
        #
        self.request_d_versicle_trigger = QAction(QIcon(":/icons/icons/nivbible.png"),"Solicitar versículo diario")
        self.request_d_versicle_trigger.triggered.connect(lambda: self.send_versicle(VersicleType.DAILY))
        self.request_r_versicle_trigger = QAction(QIcon(":/icons/icons/nivbible.png"),"Solicitar versículo al azar")
        self.request_r_versicle_trigger.triggered.connect(lambda: self.send_versicle(VersicleType.RANDOM))
        self.request_weather_trigger = QAction(QIcon(":/icons/icons/weather_clock.png"),"Solicitar clima")
        self.request_weather_trigger.triggered.connect(lambda: self.get_city())
        #self.request_translation_trigger = QAction(QIcon(":/icons/icons/google_translate.png"), "Solicitar traducción")
        self.request_web_search_trigger = QAction(QIcon(":/icons/icons/google_search (2).png"),"Solicitar búsqueda Web")
        self.request_web_search_trigger.triggered.connect(self.get_criterion)
        self.maximize_trigger = QAction(QIcon(":/rc/graphics/window_undock@2x.png"), "Maximizar")
        self.maximize_trigger.triggered.connect(self.showNormal)
        self.close_trigger = QAction(QIcon(":/rc/graphics/window_close@2x.png"), "Cerrar")
        self.close_trigger.triggered.connect(self.close)
        #
        self.menu.addAction(self.request_d_versicle_trigger)
        self.menu.addAction(self.request_r_versicle_trigger)
        self.menu.addAction(self.request_weather_trigger)
        #self.menu.addAction(self.request_translation_trigger)
        self.menu.addAction(self.request_web_search_trigger)
        self.menu.addAction(self.maximize_trigger)
        self.menu.addAction(self.close_trigger)
        #
        self.system_tray_icon.setContextMenu(self.menu)
        self.system_tray_icon.show()
        #
        self.splash.close()

    def load_last_data(self):
        # TRANSLATOR
        translator_text = SETTINGS.value("last_translator_text", type=str)
        self.text_to_translate.setPlainText(translator_text)
        # WEATHER
        city = SETTINGS.value("last_weather_city", type=str)
        self.city_input.setCurrentText(city)
        # WEB SEARCH
        # web_criterion = SETTINGS.value("last_web_search_criterion", type=str)
        # self.main_web_search_input.setText(web_criterion)

    def fill_languages(self):
        # limpio Combo Boxxs
        self.from_lang.clear()
        self.to_lang.clear()
        # agrego items
        for i in range(len(LANGUAGES)):
            prefix, lang = LANGUAGES[i]
            if not i:
                self.from_lang.addItem(f"{lang}")
            else:
                self.from_lang.addItem(f"{lang} ({prefix})")
                self.to_lang.addItem(f"{lang} ({prefix})")
        # por defecto Ingles
        self.from_lang.setCurrentIndex(0) #23 -> Ingles
        # por defecto Espannol
        self.to_lang.setCurrentIndex(89) # 90 -> Espannol | 21 -> Ingles

    def fill_municip(self):
        for municip in MUNICIPALITIES:
            self.city_input.addItem(municip)
        self.city_input.setCurrentText("")

    def load_effects(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(2)
        self.nav_toolbar.setGraphicsEffect(shadow)
        self.nav_more_widget.setGraphicsEffect(shadow)

    def connections(self):
        self.preferences_action.triggered.connect(self.show_preferences)
        # WEATHER
        self.send_city.clicked.connect(self.send_weather)
        # TRANSLATOR
        self.text_to_translate.textChanged.connect(self.translate_text_char_count)
        self.interchange_lang.clicked.connect(self.interchange_languages)
        self.send_request_translator.clicked.connect(self.send_translator)
        self.copy_translate.clicked.connect(self.copy_text_to_translate)
        self.copy_translated_text.clicked.connect(self.copy_translated_text_)
        self.delete_to_translate_text.clicked.connect(self.text_to_translate.clear)
        # VERSICLE
        self.copy_versicle.clicked.connect(self.copy_versicle_text_n_verse)
        self.save_versicle.clicked.connect(self.dowload_versicle)
        # WEB_SEARCH
        self.send_search_criterion.clicked.connect(self.start_web_request)
        self.main_send_search_criterion.clicked.connect(self.set_criterion_text)
        #
        self.web_search_info.clicked.connect(self.current_tab_info)
        self.web_search_history.clicked.connect(self.show_history)
        #
        self.navigator_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(0))
        self.translator_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        self.weather_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        self.versicle_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(3))
        self.bitcoin_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(4))
        #
        self.translator.clicked.connect(lambda: self.tab_widget.setCurrentIndex(1))
        self.weather.clicked.connect(lambda: self.tab_widget.setCurrentIndex(2))
        self.bible_verses.clicked.connect(lambda: self.tab_widget.setCurrentIndex(3))
        self.bitcoin.clicked.connect(lambda: self.tab_widget.setCurrentIndex(4))
        #
        self.changes_action.triggered.connect(self.show_changes)
        self.donate_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(5))

    def copy_to_clipboard(self, str):
        self.clipboard_ = QApplication.clipboard()
        self.clipboard_.clear()
        self.clipboard_.setText(str, QClipboard.Clipboard)

    def copy_text_to_translate(self):
        text = self.text_to_translate.toPlainText()
        self.copy_to_clipboard(text)

    def copy_translated_text_(self):
        text = self.translated_text.toPlainText()
        self.copy_to_clipboard(text)

    def copy_versicle_text_n_verse(self):
        text = self.versicle_text.text()
        verse = self.versicle_verse.text()
        self.copy_to_clipboard(f"{text}\n{verse}")

    def dowload_versicle(self):
        txt, _ = QFileDialog.getSaveFileName(self, "Guardar versículo", QDir.homePath(), "Archivo de texto (*.txt)")
        if txt:
            text = self.versicle_text.text()
            verse = self.versicle_verse.text()
            solid = f"================ VERSÍCULO ================\n{text}\n{verse}\n==========================================="
            with open(txt, "w", encoding="utf-8") as txt_file:
                txt_file.write(solid)

    def show_weather_elements(self, b=True):
        if not b:
            self.waiting_widget.setVisible(not b)
        self.weather_main.setVisible(b)
        self.details.setVisible(b)
        self.some_details.setVisible(b)

    def show_versicle_elements(self, b=True):
        self.versicle_date.setVisible(b)
        self.versicle_time.setVisible(b)
        self.versicle_text.setVisible(b)
        self.versicle_verse.setVisible(b)
        self.versicle_options.setVisible(b)

    def new_elements(self):
        # WEB HISTORY
        self.web_history = None
        # STATUS BAR
        font = QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        self.status_lbl = QLabel("Bienvenido a Coogle!")
        self.status_lbl.setFont(font)
        self.statusbar.addWidget(self.status_lbl)
        # Tiempo demorado
        # label de tiempo
        self.timer_lbl = QLabel("Detalles de operaciones :)")
        self.timer_lbl.setFont(font)
        # boton actualizar manual
        #self.update_manually = QToolButton(self)
        #self.update_manually.setAutoRaise(True)
        #self.update_manually.setText("Comprobar!")
        #self.update_manually.setEnabled(False)
        #
        self.statusbar.addPermanentWidget(self.timer_lbl)
        #self.statusbar.addPermanentWidget(self.update_manually)
        # TIMER
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_waiting_time)
        self.time = QTime(0, 0, 0)
        # weather status label SeqAnimatedLabel
        font = QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.weather_status_lbl = QLabel(self.waiting_widget)
        self.weather_status_lbl.setFont(font)
        self.weather_status_lbl.setStyleSheet("color: rgb(255, 255, 255);")
        self.weather_status_lbl.setObjectName("weather_status_lbl")
        self.weather_status_lbl.setText("Revise el clima de su ciudad")
        self.waiting_Layout.addWidget(self.weather_status_lbl, 0, 1, 1, 1, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.weather_status_icon = SeqAnimatedLabel(parent=self.waiting_widget, pixmap=":/icons/icons/about.png")
        self.weather_status_icon.setMinimumSize(QSize(30, 0))
        self.weather_status_icon.setMaximumSize(QSize(30, 30))
        self.weather_status_icon.setText("")
        self.weather_status_icon.setObjectName("weather_status_icon")
        self.waiting_Layout.addWidget(self.weather_status_icon, 0, 0, 1, 1, alignment=Qt.AlignmentFlag.AlignHCenter)
        #self.weather_status_icon.start_animation()
        # VERSICLE CONTEXT MENU
        self.versicle_context_menu = QMenu(self)
        self.versicle_context_menu.setStyleSheet(QMENU_STYLE)
        # SEND
        self.send_request_versicle.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.send_request_versicle.clicked.connect(self.versicle_send_context_menu) #customContextMenuRequested
        # OPTIONS
        self.options_versicle.clicked.connect(self.versicle_options_context_menu)

    def load_styles(self):
        #
        self.city_input.setStyleSheet(QCOMBOX_STYLE)
        self.from_lang.setStyleSheet(QCOMBOX_STYLE)
        self.to_lang.setStyleSheet(QCOMBOX_STYLE)

    def versicle_options_context_menu(self):
        try:
            self.versicle_context_menu.clear()
            # ACTIONS
            history = QAction(QIcon(":/icons/icons/history.png"), "Historial", self.versicle_context_menu)
            history.triggered.connect(self.show_versicle_history)
            #
            preferences = QAction(QIcon(":/icons/icons/preferences.png"), "Preferencias",self.versicle_context_menu)
            preferences.triggered.connect(self.versicle_preferences)
            # ADDING ACTIONS
            self.versicle_context_menu.addAction(history)
            self.versicle_context_menu.addAction(preferences)
            # ejecuto el menu
            point = QPoint(0, self.options_versicle.height())
            self.versicle_context_menu.exec_(self.options_versicle.mapToGlobal(point))
        except Exception as e:
            self.error("Mostrando menú conceptual", e.args)
            SENT_TO_LOG(f"Mostrando menú conceptual {e.args}")

    def show_versicle_history(self):
        pass

    def versicle_preferences(self):
        input = QInputDialog(self)
        #
        items = {"Reina Valeria 1960": TranslateType.VALERA1960, "Reina Valeria 1995": TranslateType.VALERA1995,
                 "Nueva Versión Internacional": TranslateType.NVI}
        actual_trans = SETTINGS.value("versicle_traduction", type=str)
        for i in items:
            if items[i].value == actual_trans:
                actual_trans = i
        label = f"Traducción actual: {actual_trans}\nSeleccione el tipo de traducción"
        traduction, ok = input.getItem(self, "Preferencias", label, tuple(items.keys()), editable=False)
        if ok:
            SETTINGS.setValue("versicle_traduction", items[traduction].value)
            SETTINGS.sync()

    def versicle_send_context_menu(self, point):
        try:
            print(point)
            self.versicle_context_menu.clear()
            # ACTIONS
            daily = QAction("Versículo diario", self.versicle_context_menu)
            daily.triggered.connect(self.set_daily_versicle)
            #
            random = QAction("Versículo aleatorio", self.versicle_context_menu)
            random.triggered.connect(self.set_random_versicle)
            # ADDING ACTIONS
            self.versicle_context_menu.addAction(daily)
            self.versicle_context_menu.addAction(random)
            # eejcuto el munu
            point = QPoint(0, self.send_request_versicle.height())
            self.versicle_context_menu.exec_(self.send_request_versicle.mapToGlobal(point))
        except Exception as e:
            self.error("Mostrando menú conceptual", e.args)
            SENT_TO_LOG(f"Mostrando menú conceptual {e.args}")

    def start_timer(self, again=False):
        #if again:
        self.time = QTime(0, 0, 0)
        self.timer.start(1000)

    def update_waiting_time(self):
        self.time = self.time.addSecs(1)
        self.timer_lbl.setText(f"Tiempo esperado: {self.time.toString('hh:mm:ss')}")

    def error(self, place, text):
        # logs
        SENT_TO_LOG(text)
        #
        self.timer.stop()
        #
        self.status_lbl.setText("Error!")
        msg = QMessageBox()
        # msg.setStyleSheet(DARK_STYLE)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Error")
        msg.setText("Ha ocurrido un error!")
        msg.setInformativeText(f"-> {place}")
        msg.setDetailedText(str(text))
        msg.exec_()

    def check_auth(self):
        user = SETTINGS.value("current_user", type=str)
        if user:
            return True
        self.error("No puede usar el servicio Coogle", "Primero debe configurar una cuenta de correo para usar.\nDiríjase a Preferencias, inserte un correo y su respectiva contraseña y presione el botón de autenticación para completar el proceso.")
        return False

    def get_user(self):
        try:
            user = SETTINGS.value("current_user", type=str)
            user_from_bd = SELECT_ONE_USER(user)
            passw = user_from_bd.decode_passw()
            return user, passw
        except Exception as e:
            self.error("Obteniendo datos del usuario", e.args)

    # WEATHER
    def get_city(self):
        input = QInputDialog(self)
        city, ok = input.getItem(self, "Solicitar clima con Coogle", "Escribe el nombre de la ciudad", MUNICIPALITIES, editable=True)
        if ok:
            self.city_input.setCurrentText(city)
            self.send_weather()

    def send_weather(self):
        try:
            city = self.city_input.currentText().strip()
            if self.check_auth():
                if city:
                    # oculto los elementos
                    self.show_weather_elements(False)
                    #
                    w = WeatherRequestThread(*self.get_user(), city)
                    # signals
                    w.send_request_signal.connect(self.action_weather_status)
                    w.check_mailbox_signal.connect(self.action_weather_status)
                    w.check_content_signal.connect(self.action_weather_status)
                    w.error_signal.connect(self.error)
                    w.finish_signal.connect(self.set_weather_data)
                    # launch thread
                    task = threading.Thread(target=w.run)
                    task.start()
                    # add task
                    self.weather_requests.append(task)
                    # inicio timer
                    self.start_timer()
        except Exception as e:
            self.error("Error solicitando el clima", e.args)

    def action_weather_status(self, i, success, message, details, icon, critical=False):
        self.weather_status_lbl.setText(message)
        self.weather_status_icon.setPixmap(QPixmap(icon))
        if not success:
            if critical:
                self.timer.stop()
        if details:
            self.status_lbl.setText(details)

    def set_weather_data(self, weather:Weather):
        SETTINGS.setValue("succesfully_weather_request", False)
        if weather.FOUNDED:
            SETTINGS.setValue("succesfully_weather_request", True)
            #
            self.weather_status_lbl.setText("Mostrando datos...")
            self.weather_status_icon.set_animation_type(AnimType.RECEIVED_WEATHER)
            self.weather_status_icon.start_animation()#setPixmap(QPixmap(":/icons/icons/about.png"))
            #
            self.clouds_layer = weather.clouds_layer
            self.background.setStyleSheet(weather.sky_color.value)
            self.repaint()
            #
            self.show_weather_elements()
            #
            self.city.setText(weather.criterion)
            self.city.setToolTip(f"Latitud: {weather.lat} Longitud: {weather.long}")
            #
            self.date.setText(weather.datetime.strftime("%I:%M %p %A, %d de %B del %Y"))
            #
            self.temp.setText(str(round(weather.temp)) + "º")
            #
            pix = QPixmap(weather.icon)
            self.weather_icon.setPixmap(pix)
            self.weather_descrip.setText(weather.weather)
            #
            self.temp_max.setText(str(round(weather.max_temp, 2)) + "º")
            self.temp_min.setText(str(round(weather.min_temp, 2)) + "º")
            self.feels_like.setText(str(round(weather.feels_like, 2)) + "º")
            self.sea_lvl.setText(str(weather.sea_lvl) + "m")
            self.ground_lvl.setText(str(weather.ground_lvl) + "m")
            #
            country = weather.country
            self.country.setText(country)
            #
            self.wind.setText(str(round(weather.wind, 1)) + " Km/h")
            self.pressure.setText(str(weather.pressure) + " Pa")
            self.humidity.setText(str(weather.humidity) + " %")
            self.sunrise.setText(str(weather.sunrise.strftime("%I:%M %p")))
            self.sunset.setText(str(weather.sunset.strftime("%I:%M %p")))
            #
            # guardar en cache
            try:
                INSERT_WEATHER(weather)
            except Exception as e:
                self.error("Guardando cache", f"No se pudo guardar el archivo de cache {e.args}")
            SAVE_SETTINGS("last_weather_city", weather.criterion)
            # reinicio timer
            self.timer.stop()
            # notificate
            icon = QIcon(pix)
            self.system_tray_icon.showMessage("Clima obtenido",
                                              f"Ciudad: {weather.criterion}\nTemperatura: {weather.temp} Cº\nClima: {weather.weather}\nTamaño: {nz(weather.size)}\nTiempo demorado: {self.time.toString('hh:mm:ss')}",
                                              icon)

            def go_to():
                self.showNormal()
                self.tab_widget.setCurrentIndex(2)

            self.system_tray_icon.messageClicked.connect(lambda: go_to())
# >---------------------------------------------------------------------------------------------------------------< #
    # VERSICLES
    def set_daily_versicle(self):
        self.send_versicle(VersicleType.DAILY)

    def set_random_versicle(self):
        self.send_versicle(VersicleType.RANDOM)

    def send_versicle(self, type):
        if self.check_auth():
            # oculto los elements
            self.show_versicle_elements(False)
            #
            translate_to = SETTINGS.value("versicle_traduction", type=str)
            #
            v = VersicleRequestThread(*self.get_user(), type, translate_to)
            # signals
            v.send_request_signal.connect(self.action_versicle_status)
            v.check_mailbox_signal.connect(self.action_versicle_status)
            v.check_content_signal.connect(self.action_versicle_status)
            v.error_signal.connect(self.error)
            v.finish_signal.connect(self.set_versicle_data)
            # launch thread
            task = threading.Thread(target=v.run)
            task.start()
            self.versicles_requests.append(task)
            # inicio timer
            self.start_timer()

    def action_versicle_status(self, i, success, message, details, icon, critical=False):
        self.versicle_status_lbl.setText(message)
        self.versicle_status_icon.setPixmap(QPixmap(icon))
        if not success:
            if critical:
                self.timer.stop()
                #first = self.versicles_requests.pop()
                #self.versicles_requests.append(first)
        if details:
            self.status_lbl.setText(details)

    def set_versicle_data(self, versicle: Versicle):
        if versicle.FOUNDED:
            #
            self.versicle_status_lbl.setText("Mostrando datos...")
            self.versicle_status_icon.setPixmap(QPixmap(":/icons/icons/about.png"))
            #
            self.show_versicle_elements()
            # fecha y hora
            date = versicle.creation_date.date()
            self.versicle_date.setText(date.strftime("%d %B, %Y"))
            time = versicle.creation_date.time()
            self.versicle_time.setText(time.strftime("%I:%M %p"))
            # texto
            text = versicle.text
            self.versicle_text.setText(text)
            # verso en el que se encuentra
            verse = versicle.verse
            self.versicle_verse.setText(verse)
            #
            self.versicle_status_lbl.setText("Hecho!")
            self.versicle_status_icon.setPixmap(QPixmap(":/icons/icons/success_green.png"))
            # guardar en cache
            try:
                INSERT_VERSICLE(versicle)
            except Exception as e:
                self.error("Guardando cache", f"No se pudo guardar el archivo de cache {e.args}")
            # reinicio timer
            self.timer.stop()
            # notificate
            icon = QIcon(":/icons/icons/nivbible.png")
            self.system_tray_icon.showMessage("Versículo encontrado",
                                              f"{versicle.text[:20]}...\n{versicle.verse}\nTamaño: {nz(versicle.size)}\nTiempo demorado: {self.time.toString('hh:mm:ss')}",
                                              icon)

            def go_to():
                self.showNormal()
                self.tab_widget.setCurrentIndex(3)
            self.system_tray_icon.messageClicked.connect(lambda: go_to())

# >---------------------------------------------------------------------------------------------------------------< #
    # TRANSLATOR
    def interchange_languages(self):
        actual_from = self.from_lang.currentIndex()
        # si no esta seleccionada la identificacion de idioma
        if actual_from != 0:
            actual_to = self.to_lang.currentIndex()
            #
            self.from_lang.setCurrentIndex(actual_to + 1)
            self.to_lang.setCurrentIndex(actual_from - 1)

    def translate_text_char_count(self):
        text = self.text_to_translate.toPlainText()
        len_text = len(text)
        if len_text > 900:
            self.text_to_translate.setPlainText(text[:-1])
            cursor = self.text_to_translate.textCursor()
            cursor.setPosition(900)
            self.text_to_translate.setTextCursor(cursor)
        self.char_count.setText(f"{len(self.text_to_translate.toPlainText())}/900")

    def send_translator(self):
        if self.check_auth():
            #
            text = self.text_to_translate.toPlainText().strip()
            # registro el texto como borrador
            SAVE_SETTINGS("last_translator_text", text)
            #
            from_lang = LANGUAGES[self.from_lang.currentIndex()]
            to_lang = LANGUAGES[self.to_lang.currentIndex()+1]
            #
            t = TranslatorRequestThread(*self.get_user(), text, from_lang, to_lang)
            # signals
            t.send_request_signal.connect(self.action_translator_status)
            t.check_mailbox_signal.connect(self.action_translator_status)
            t.check_content_signal.connect(self.action_translator_status)
            t.error_signal.connect(self.error)
            t.finish_signal.connect(self.set_translator_data)
            # launch thread
            task = threading.Thread(target=t.run)
            task.start()
            # add task
            self.translation_requests.append(task)
            # inicio timer
            self.start_timer()
            # limpio interfaz
            self.translated_text.setPlainText("")
            self.translate_details.setText("Detalles de la traducción")

    def action_translator_status(self, i, success, message, details, icon, critical=False):
        self.translator_status_lbl.setText(message)
        self.translator_status_icon.setPixmap(QPixmap(icon))
        if not success:
            if critical:
                self.timer.stop()
        if details:
            self.status_lbl.setText(details)

    def set_translator_data(self, translator: Translator):
        SAVE_SETTINGS("succesfully_translator_request", False)
        if translator.FOUNDED:
            SAVE_SETTINGS("succesfully_translator_request", True)
            #
            self.translator_status_lbl.setText("Mostrando datos...")
            self.translator_status_icon.setPixmap(QPixmap(":/icons/icons/about.png"))
            # idioma original -> idioma traduccion
            from_lang = translator.from_
            to_lang = translator.to_
            self.translate_details.setText(f"{from_lang[0]} ({from_lang[1]}) -> {to_lang[0]} ({to_lang[1]})")
            # texto traducido
            translated_text = translator.translation
            self.translated_text.setPlainText(translated_text)
            # status
            self.translator_status_lbl.setText("Hecho!")
            self.translator_status_icon.setPixmap(QPixmap(":/icons/icons/success_green.png"))
            # guardar en cache
            try:
                INSERT_TRANSLATION(translator)
            except Exception as e:
                self.error("Guardando cache", f"No se pudo guardar el archivo de cache {e.args}")
            # registro el texto
            SAVE_SETTINGS("last_translator_text", "")
            # reinicio timer
            self.timer.stop()
            # notificate
            icon = QIcon(":/icons/icons/google_translate (2).png")
            self.system_tray_icon.showMessage("Traducción encontrada",
                                              f"{translator.from_[1]}: {translator.to_[1]}\n{translator.translation[:20]}...\nTamaño: {nz(translator.size)}\nTiempo demorado: {self.time.toString('hh:mm:ss')}",
                                              icon)
            def go_to():
                self.showNormal()
                self.tab_widget.setCurrentIndex(1)
            self.system_tray_icon.messageClicked.connect(lambda: go_to())

    # >---------------------------------------------------------------------------------------------------------------< #
    # WEB SEARCH
    def set_web_search_completer(self):
        searches = GET_SEARCHES()
        if searches is not None:
            my_completer = QCompleter(searches, self)
            my_completer.setCaseSensitivity(0)
            self.web_search_input.setCompleter(my_completer)

    def create_tab(self, web_search):
        title = web_search.criterion
        founded = web_search.FOUNDED
        # title
        if len(title) > 20:
            title = title[:20] + "..."
        #
        s_e = web_search.engine#self.get_search_engine()
        r_t = web_search.request_type#self.get_request_type()
        icon = QIcon()
        if s_e == SearchEngine.GOOGLE:
            icon.addPixmap(QPixmap(":/icons/icons/google.png"))
        elif s_e == SearchEngine.WIKIPEDIA:
            icon.addPixmap(QPixmap(":/icons/icons/wikipedia (2).png"))
        elif s_e == SearchEngine.BING:
            icon.addPixmap(QPixmap(":/icons/icons/bing (2).png"))
        elif r_t == RequestType.PDF:
            icon.addPixmap(QPixmap(":/icons/icons/pdf_viewer.png"))
        # annadir qwebview
        web_view = WebSearchPage(self.web_search_tab, founded)
        web_view.new_request.connect(self.send_web_search)
        web_view.set_web_content(
            """<html><head/><body><p align="center"><img src=":/logo/designs.png" /></p><p align="center"><span style=" font-family:'Product Sans'; font-size:35pt; font-weight:600; color:#c3c3c3;">Coogle</span></p><p align="center"><span style=" font-family:'Product Sans'; font-size:25pt; font-weight:600; color:#868686;">Esperando respuesta...</span></p></body></html>""")
        # si no ha sido encotrado el resutado pues
        if not founded:
            # inicio timer
            web_view.start_timer()
        else:
            web_view.set_status(f"Tamaño: {nz(web_search.size) if web_search.size is not None else '-'}")
            web_view.set_status_time(f"Tiempo demorado: {web_search.elapsed_time if web_search.size is not None else '--:--:--'}")
        # add tab
        self.web_search_tab.addTab(web_view, icon, title) #http://www.google.com/url?q=https://forum.qt.io/topic/126003/qwebengineview-to-view-local-pdf-at-certain-page&sa=U&ved=2ahUKEwjx0KCDkKXxAhUIgK0KHUGFC_4QFjACegQIHxAB&usg=AOvVaw2xs3PCSIOnqPBAA-AMrJy0

    def close_tab(self, idx):
        if self.web_search_tab.count() > 1:
            self.web_search_requests.pop(idx)
            self.web_search_tab.removeTab(idx)
            self.update_tab_idx()

    def show_tab(self, i):
        self.showNormal()
        self.tab_widget.setCurrentIndex(0)
        self.web_search_tab.setCurrentIndex(i)

    def current_tab_info(self):
        web_page = self.web_search_tab.currentWidget()
        if isinstance(web_page, WebSearchPage):
            web_page.show_hide_info()

    def update_tab_idx(self):
        #for i in range(len(self.web_search_requests)):
            #self.web_search_requests[i].set_i(i)
            #print(self.web_search_requests[i].i)
            #print(self.web_search_requests[i].w_s.i)
        pass

    def set_criterion_text(self):
        if self.check_auth():
            # critrio
            main_search_text = self.main_web_search_input.text()
            if main_search_text:
                self.web_search_input.setText(main_search_text)
                self.main_web_search_input.setText("")
            #
            self.web_search_requests.pop()
            self.web_search_tab.removeTab(0)
            #
            self.start_web_request()

    def get_search_engine(self):
        idx = self.web_search_engine.currentIndex()
        if idx == 0:
            return SearchEngine.GOOGLE
        elif idx == 1:
            return SearchEngine.GOOGLE_IMG
        elif idx == 2:
            return SearchEngine.WIKIPEDIA
        elif idx == 3:
            return SearchEngine.BING
        elif idx == 4:
            return SearchEngine.YAHOO
        elif idx == 5:
            return ""#SearchEngine.YANDEX

    def get_request_type(self):
        idx = self.web_search_request_type.currentIndex()
        if idx == 0:
            return RequestType.HTML
        elif idx == 1:
            return RequestType.TEXT
        elif idx == 2:
            return RequestType.FULL_HTML
        elif idx == 3:
            return RequestType.PDF

    def start_web_request(self):
        criterion = self.web_search_input.text().strip()
        self.send_web_search(criterion)

    def get_criterion(self):
        input = QInputDialog(self)
        criterion, ok = input.getText(self, "Buscar en Internet con Coogle", "¿Qué deseas buscar?")
        if ok:
            self.send_web_search(criterion)

    def send_web_search(self, criterion, only_receive=False):
        # cehquear que haya una cuenta para recibir correos
        if self.check_auth():
            if criterion:
                #
                if only_receive:
                    web_search = criterion
                    #
                    user, passw = self.get_user()
                    #
                    web_search.user = user
                    web_search.passw = passw
                    w_b = WebSearchRequestThread(web_search)
                    criterion = web_search.criterion
                else:
                    engine = self.get_search_engine()
                    request_type = self.get_request_type()
                    results = int(self.web_search_results_q.currentText())
                    web_search = WebSearch(*self.get_user(), criterion, engine, request_type, results)
                    w_b = WebSearchRequestThread(web_search)
                # idx
                w_b.set_i(len(self.web_search_requests))
                # signals
                w_b.send_request_signal.connect(self.action_web_search_status)
                w_b.check_mailbox_signal.connect(self.action_web_search_status)
                w_b.check_content_signal.connect(self.action_web_search_status)
                w_b.error_signal.connect(self.error)
                w_b.finish_signal.connect(self.set_web_search_data)
                # launch thread
                task = threading.Thread(target=w_b.run, args=(only_receive,))
                task.start()
                # add task
                self.web_search_requests.append(task)
                # add tab
                self.create_tab(web_search)
                self.web_search_tab.setTabsClosable(True)
                # adding web search to DB
                try:
                    INSERT_WEB_SEARCH(w_b.w_s)
                except Exception as e:
                    print(e.args)

    def action_web_search_status(self, i, success, message, details, icon, critical=False):
        web_page:WebSearchPage = self.web_search_tab.widget(i)
        web_page.set_request_state(message)
        web_page.set_request_state_icon(QPixmap(icon))
        if message == "Datos recibidos":
            web_page.set_web_content("""<html><head/><body><p align="center"><img src=":/logo/designs.png"/></p><p align="center"><span style=" font-family:'Calibri'; font-size:24pt; font-weight:600; color:#c3c3c3;">Cargando...</span></p></body></html>""")
        if not success:
            if critical:
                self.timer.stop()
                #web_page.set_retry(True)
        if details:
            web_page.set_status(details)

    def set_web_search_data(self, web_search: WebSearch):
        if web_search.FOUNDED:
            #
            i = web_search.i
            web_page: WebSearchPage = self.web_search_tab.widget(i)
            #
            web_page.set_request_state("Mostrando datos...")
            web_page.set_request_state_icon(QPixmap(":/icons/icons/about.png"))
            # html source
            if web_search.request_type == RequestType.HTML:
                html = web_search.html
                web_page.set_web_content(html)
            elif web_search.request_type == RequestType.FULL_HTML:
                file = web_search.path_attachment
                web_page.set_web_file(file)
            elif web_search.request_type == RequestType.PDF:
                file = web_search.path_attachment
                web_page.set_pdf_file(file)
            #
            # status
            web_page.set_request_state(web_search.criterion)
            web_page.set_request_state_icon(QPixmap(":/icons/icons/success_green.png"))
            # ocultar status
            web_page.show_hide_info()
            # guardar en cache
            try:
                web_search.elapsed_time = web_page.qtime.toString()
                UPDATE_WEB_SEARCH(web_search)
            except Exception as e:
                self.error("Guardando cache", f"No se pudo guardar el archivo de cache {e.args}")
            # actualizar historial
            if self.web_history is not None:
                self.web_history.load_history()
            # regsitro ultima busqueda
            SAVE_SETTINGS("last_web_search_criterion", web_search.criterion)
            # reinicio timer
            web_page.timer.stop()
            # alert
            play_audio("sound/okay.wav")
            icon = self.web_search_tab.tabIcon(i)
            self.system_tray_icon.showMessage("Respuesta encontrada",
                                              f"{web_search.engine.name}: {web_search.criterion}\nTamaño: {nz(web_search.size)}\nTiempo demorado: {web_page.qtime.toString('hh:mm:ss')}",
                                              icon)

            self.system_tray_icon.messageClicked.connect(lambda: self.show_tab(i))

    def show_history(self):
        if self.web_history is None:
            self.web_history = History(self)
            self.web_history.new_request.connect(lambda a: self.send_web_search(a, True))
            self.web_history.open_file.connect(self.open_web_file)
        self.web_history.load_history()
        self.web_history.show()

    def open_web_file(self, webSearch):
        self.create_tab(webSearch)
        i = self.web_search_tab.count() - 1
        web_page: WebSearchPage = self.web_search_tab.widget(i)
        #
        if webSearch.request_type == RequestType.HTML:
            html = webSearch.html
            web_page.set_web_content(html)
        elif webSearch.request_type == RequestType.FULL_HTML:
            file = webSearch.path_attachment
            web_page.set_web_file(file)
        elif webSearch.request_type == RequestType.PDF:
            file = webSearch.path_attachment
            web_page.set_pdf_file(file)
        self.web_search_requests.append(None)

    def repaint(self):
        clouds = QPixmap(self.clouds_layer.value)
        clouds = clouds.scaled(self.clouds.size(), Qt.AspectRatioMode.IgnoreAspectRatio)
        pal = self.clouds.palette()
        pal.setBrush(QPalette.Background, QBrush(clouds))
        self.clouds.setPalette(pal)

    def show_preferences(self):
        self.pref = Preferences(self)
        self.pref.show()

    def show_changes(self):
        self.changes = ChangesLOG()
        self.changes.show()

def main():
    app = QApplication(argv)
    window = Coogle()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
