import subprocess

from PyQt5.QtCore import Qt, QTimer, QTime, QUrl, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpacerItem, QSizePolicy, QToolButton, \
    QPushButton, QMessageBox

from ui.clickableLabel import QLabelClickable
from util.const import HISTORY_TOOLBUTTON_STYLE
from util.logger import SENT_TO_LOG

class CustomWebEnginePage(QWebEnginePage):
    linkClicked = pyqtSignal(str)
    def acceptNavigationRequest(self, url,  _type, isMainFrame):
        print(url, _type, isMainFrame)
        if _type == QWebEnginePage.NavigationTypeLinkClicked:
            url_to_string = url.toString()
            self.linkClicked.emit(url_to_string)
            return False
        return super().acceptNavigationRequest(url, _type, isMainFrame)

class WebSearchPage(QWidget):
    new_request = pyqtSignal(object)
    def __init__(self, parent=None, founded=False):
        QWidget.__init__(self)
        self.parent = parent
        self.setContentsMargins(0, 0, 0, 0)
        # timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_waiting_time)
        self.qtime = QTime(0, 0, 0)
        #
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(0)
        # request status bar
        self.request_status_bar = QWidget(self)
        self.request_status_bar.setStyleSheet("background-color: black;\n"
                                              "border-top-left-radius: 10px;\n"
                                              "border-top-right-radius: 10px;\n")
        self.request_status_bar.setMaximumHeight(50)
        #
        self.request_status_bar_layout = QHBoxLayout(self.request_status_bar)
        #
        self.request_state_icon = QLabel(self.request_status_bar)
        self.request_state_icon.setMaximumSize(30, 30)
        self.request_state_icon.setMinimumSize(30, 30)
        self.request_state_icon.setScaledContents(True)
        self.request_state_icon.setPixmap(QPixmap(":/icons/icons/google_search.png"))
        #
        self.request_state = QLabel(self.request_status_bar)
        self.request_state.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard)
        self.request_state.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.request_state.setWordWrap(True)
        self.request_state.setStyleSheet("color: rgb(255, 255, 255);\n"
                                         'font: 12pt "Segoe UI"')
        self.request_state.setText("Esperando...")
        #
        self.retry_button = QToolButton(self.request_status_bar)
        self.retry_button.setAutoRaise(True)
        self.retry_button.setText("Reintentar")
        p = QPixmap(":/icons/icons/retry.png")
        icon = QIcon(p)
        self.retry_button.setIcon(icon)
        self.retry_button.setFixedSize(43, 43)
        self.retry_button.setStyleSheet(HISTORY_TOOLBUTTON_STYLE)
        self.show_retry_button(False)
        #
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        self.request_status_bar_layout.addWidget(self.request_state_icon)
        self.request_status_bar_layout.addWidget(self.request_state)
        self.request_status_bar_layout.addItem(spacer)
        self.request_status_bar_layout.addWidget(self.retry_button)
        #
        self.request_status_bar.setLayout(self.request_status_bar_layout)
        # q web engine
        #self.web_engine_widget = QWidget()
        self.web_engine = QWebEngineView()
        #self.web_engine.installEventFilter(self)
        # status bar
        self.status_bar = QWidget(self)
        self.status_bar.setContentsMargins(9, 0, 9, 0)
        self.status_bar.setMaximumHeight(20)
        self.status_bar.setStyleSheet("background-color: black;\n"
                                      "border-bottom-left-radius: 10px;\n"
                                      "border-bottom-right-radius: 10px;\n")
        #
        self.status_bar_layout = QHBoxLayout(self.request_status_bar)
        self.status_bar_layout.setContentsMargins(0, 0, 0, 0)
        #
        self.state = QLabel(self.request_status_bar)
        self.state.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.state.setStyleSheet("color: rgb(255, 255, 255);\n"
                                         'font: bold 12pt "Segoe UI"')
        self.state.setText("Esperando...")
        #
        self.time = QLabel(self.request_status_bar)
        self.time.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.time.setStyleSheet("color: rgb(255, 255, 255);\n"
                                         'font: bold 12pt "Segoe UI"')
        self.time.setText("--:--:--")
        #
        spacer2 = QSpacerItem(40, 20, QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        self.status_bar_layout.addWidget(self.state)
        self.status_bar_layout.addItem(spacer2)
        self.status_bar_layout.addWidget(self.time)
        #
        self.status_bar.setLayout(self.status_bar_layout)
        #
        self.main_layout.addWidget(self.request_status_bar)
        self.main_layout.addWidget(self.web_engine)
        self.main_layout.addWidget(self.status_bar)
        # if founded
        if founded:
            self.request_state.setText("Archivo cargado!")
            self.request_state_icon.setPixmap(QPixmap(":/icons/icons/success_green.png"))

    def show_retry_button(self, b=True):
        self.retry_button.setVisible(b)

    # def eventFilter(self, source, event):
    #     if (event.type() == QEvent.Type.ChildAdded and source is self.web_engine and event.child().isWidgetType()):
    #         self._glwidget = event.child()
    #         self._glwidget.installEventFilter(self)
    #     elif (event.type() == QEvent.Type.MouseButtonPress and
    #           source is self._glwidget):
    #         print('web-view mouse-press:', event.pos())
    #     return super().eventFilter(source, event)

    def show_hide_info(self):
        if self.status_bar.isVisible():
            self.request_status_bar.hide()
            self.status_bar.hide()
        else:
            self.request_status_bar.show()
            self.status_bar.show()

    def set_page(self, url):
        page = CustomWebEnginePage(self)
        page.linkClicked.connect(self.emit_new_request)
        page.setUrl(QUrl(url))
        self.web_engine.setPage(page)

    def emit_new_request(self, url):
        self.new_request.emit(url)

    def set_web_content(self, html):
        self.web_engine.setHtml(html)

    def set_web_file(self, file):
        #with open(file, "rb") as file:
        url = QUrl.fromLocalFile(file)
        self.set_page(url)
        #soup = BeautifulSoup(file, "html.parser")
        #self.web_engine.setHtml(soup.decode_contents())

    def set_pdf_file(self, file):
        self.file = file
        # url = QUrl.fromLocalFile(file)
        # self.set_page(url)
        self.web_engine.hide()
        self.open_pdf = QLabelClickable(self)
        self.open_pdf.setText("Abrir archivo PDF")
        self.main_layout.insertWidget(1, self.open_pdf)
        self.open_pdf.clicked.connect(self.open_pdf_link)

    def open_pdf_link(self):
        try:
            CREATE_NO_WINDOW = 0x08000000
            subprocess.Popen(['cmd', '/C', 'start', self.file, self.file],
                             stderr=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stdin=subprocess.PIPE,
                             shell=False,
                             creationflags=CREATE_NO_WINDOW)
        except Exception as e:
            self.error("Abriendo archivo PDF", e.args)
        # if folder:
        #     file_path = file_path.replace("/", "\\")
        #     subprocess.Popen(['explorer.exe', file_path],
        #                      stderr=subprocess.PIPE,
        #                      stdout=subprocess.PIPE,
        #                      stdin=subprocess.PIPE,
        #                      shell=False,
        #                      creationflags=CREATE_NO_WINDOW)
        # else:
        #     i = self.lista_descargas.currentRow()
        #     if i != -1:
        #         item = self.elementos[i]
        #         file_path = os.path.join(item.dir_descarga, item.txt, item.nombre_archivo)
        #         file_path = file_path.replace("/", "\\")
        #         if highlight:
        #             subprocess.Popen(['explorer.exe', '/select,', file_path],
        #                              stderr=subprocess.PIPE,
        #                              stdout=subprocess.PIPE,
        #                              stdin=subprocess.PIPE,
        #                              shell=False,
        #                              creationflags=CREATE_NO_WINDOW)
        #
        #         else:

    def set_request_state(self, text):
        self.request_state.setText(text)

    def set_request_state_icon(self, icon):
        self.request_state_icon.setPixmap(icon)

    def set_status(self, text):
        self.state.setText(text)

    def set_status_time(self, time):
        self.time.setText(time)

    def start_timer(self):
        self.qtime = QTime(0, 0, 0)
        self.timer.start(1000)

    def update_waiting_time(self):
        self.qtime = self.qtime.addSecs(1)
        self.set_status_time(f"Tiempo esperado: {self.qtime.toString('hh:mm:ss')}")

    def error(self, place, text):
        # logs
        SENT_TO_LOG(text)
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