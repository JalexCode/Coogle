from PyQt5.QtCore import QSize, QMetaObject, Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QAbstractItemView, QSizePolicy, QListWidget, QListWidgetItem, \
    QGridLayout, QToolButton, QWidget, QHBoxLayout, QLineEdit, QMessageBox, QSpacerItem

from util.cache_db import GET_HISTORY
from util.const import HISTORY_TOOLBUTTON_STYLE, HISTORY_LIST_STYLE, nz
import ui.resources
TOOL_BUTTON_STYLE = """QToolButton{
    background-color: transparent;
    border-radius: 5px;
}
QToolButton:hover{
    background-color: rgb(0, 221, 255);
}"""
class QCustomListItem(QWidget):
    refresh = pyqtSignal(int)
    request_info = pyqtSignal(int)
    def __init__(self, parent=None):
        QWidget.__init__(self)
        self.parent = parent
        self.__i = 0
        # init
        self.setObjectName("ItemWidget")
        self.resize(598, 60)
        #self.setMaximumSize(QSize(16777215, 60))
        font = QFont()
        font.setFamily("Calibri")
        font.setPointSize(10)
        self.setFont(font)
        self.gridLayout_2 = QGridLayout(self)
        self.gridLayout_2.setObjectName("gridLayout_2")
        # info button
        self.info_button = QToolButton(self)
        self.info_button.setStyleSheet(TOOL_BUTTON_STYLE)
        icon = QIcon()
        icon.addPixmap(QPixmap(":/icons/icons/about_white.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.info_button.setIcon(icon)
        self.info_button.setIconSize(QSize(30, 30))
        self.info_button.setAutoRaise(True)
        self.info_button.setObjectName("info_button")
        self.gridLayout_2.addWidget(self.info_button, 0, 2, 1, 1)
        # download button
        self.download = QToolButton(self)
        self.download.setStyleSheet(TOOL_BUTTON_STYLE)
        icon = QIcon()
        icon.addPixmap(QPixmap(":/icons/icons/retry_icon.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.download.setIcon(icon)
        self.download.setIconSize(QSize(30, 30))
        self.download.setAutoRaise(True)
        self.download.setObjectName("download")
        # adding to layout
        self.gridLayout_2.addWidget(self.download, 0, 3, 1, 1)
        # status icon
        self.icon = QLabel(self)
        self.icon.setMinimumSize(QSize(40, 40))
        self.icon.setMaximumSize(QSize(40, 40))
        font = QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.icon.setFont(font)
        self.icon.setText("")
        self.icon.setPixmap(QPixmap(":/icons/icons/G.png"))
        self.icon.setScaledContents(True)
        self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon.setObjectName("icon")
        self.gridLayout_2.addWidget(self.icon, 0, 0, 1, 1)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.Solicitud = QLineEdit(self)
        font = QFont()
        font.setFamily("Calibri")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.Solicitud.setFont(font)
        self.Solicitud.setObjectName("Solicitud")
        self.Solicitud.setStyleSheet("color: white;\n"
                                     "background-color:transparent;\n"
                                     "border:none;")
        self.Solicitud.setReadOnly(True)
        self.gridLayout.addWidget(self.Solicitud, 0, 0, 1, 1)
        self.info = QLineEdit(self)
        font = QFont()
        font.setFamily("Calibri")
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(50)
        self.info.setFont(font)
        self.info.setObjectName("info")
        self.info.setStyleSheet("color: white;\n"
                                     "background-color:transparent;\n"
                                     "border:none;")
        self.info.setReadOnly(True)
        self.gridLayout.addWidget(self.info, 1, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 1, 1, 1)
        # meta object
        QMetaObject.connectSlotsByName(self)
        # connections
        self.info_button.clicked.connect(lambda: self.request_info.emit(self.__i))
        self.download.clicked.connect(lambda: self.refresh.emit(self.__i))

    def set_i(self, i):
            self.__i = i

    def set_title(self, text):
        self.Solicitud.setText(text)
        self.Solicitud.setCursorPosition(0)

    def set_url(self, url):
        self.info.setText(url)
        self.info.setCursorPosition(0)

    def set_icon(self, icon):
        self.icon.setPixmap(QPixmap(icon))

class QCustomListWidget(QListWidget):
    request_info = pyqtSignal(int)
    new_request = pyqtSignal(int)
    def __init__(self, QCustomWidget):
        QListWidget.__init__(self)
        self.QCustomWidget = QCustomWidget
        # Customize SizePolicy
        self.setMinimumWidth(QCustomWidget().minimumWidth() + 30)
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding,
                                 QSizePolicy.Preferred)
        self.setSizePolicy(sizePolicy)
        # multi selection
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # set frameless
        self.setFrameShape(0)

    def add_default_items(self, num):
        for j in range(num):
            newItem = self.QCustomWidget()
            self.add_item(newItem)

    def add_item(self, newItemWidget):
        newItemWidget.i = self.count()
        # Create QListWidgetItem
        myQListWidgetItem = QListWidgetItem(self)
        # Set size hint
        myQListWidgetItem.setSizeHint(newItemWidget.sizeHint())
        # Add QListWidgetItem into QListWidget
        self.addItem(myQListWidgetItem)
        self.setItemWidget(myQListWidgetItem, newItemWidget)

    def set_itemData(self, j, data, strFlag=False):
        self.itemWidget(self.item(j)).set_data(data, strFlag)

    def set_item_idx(self, j, idx):
        self.itemWidget(self.item(j)).i = idx

    def get_itemData(self, j):
        itemWidget = self.itemWidget(self.item(j))
        if type(itemWidget) is self.QCustomWidget:
            return itemWidget.get_data()
        else:
            return None

    def get_item(self, j):
        return self.itemWidget(self.item(j))

    def set_data(self, initializationData):
        self.clear()
        for i in range(len(initializationData)):
            data = initializationData[i]
            newItem = self.QCustomWidget()
            # setting data
            icon = ":/icons/icons/warning_QR.png"
            if data.FOUNDED:
                if data.engine.name == "GOOGLE":
                    icon = ":/icons/icons/G.png"
                elif data.engine.name == "WIKIPEDIA":
                    icon = ":/icons/icons/wikipedia (2).png"
                elif data.engine.name == "BING":
                    icon = ":/icons/icons/bing (2).png"
                elif data.engine.name == "GOOGLE_IMG":
                    icon = ":/icons/icons/pdf_viewer.png"
            newItem.set_icon(icon)
            #
            criterion = data.criterion
            newItem.set_title(criterion)
            #
            url = data.url
            newItem.set_url(url)
            # button icon
            if data.FOUNDED:
                newItem.download.setVisible(False)
                #newItem.info_button.setVisible(True)
            else:
                newItem.download.setVisible(True)
                #newItem.info_button.setVisible(False)
            # set_idx
            newItem.set_i(i)
            # connection
            newItem.request_info.connect(self.show_info)
            newItem.refresh.connect(self.refresh_request)
            # adding to list
            self.add_item(newItem)

    def show_info(self, i):
        print(i)
        self.request_info.emit(i)

    def refresh_request(self, i):
        print(i)
        self.new_request.emit(i)

    def get_data(self):
        data = []
        for j in range(self.count()):
            data.append(self.get_itemData(j))
        return data

class History(QDialog):
    new_request = pyqtSignal (object)
    open_file = pyqtSignal (object)
    def __init__(self, parent=None):
        self.parent = parent
        # init super()
        QDialog.__init__(self)
        # setting window
        # size
        self.setFixedSize(710, 670)
        self.setObjectName("HistoryDialog")
        self.setStyleSheet("background-color: rgb(63, 63, 63);\n")
        self.setWindowIcon(QIcon(QPixmap(":/icons/icons/clock5.png")))
        self.setModal(True)
        # title
        self.setWindowTitle("Historial de búsquedas")
        # main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        # list
        self.history_list = QCustomListWidget(QCustomListItem)
        # list connections
        self.history_list.request_info.connect(self.show_info)
        self.history_list.new_request.connect(self.send_new_request)
        self.history_list.itemDoubleClicked.connect(self.open_file_response)
        # list's style
        self.history_list.setStyleSheet(HISTORY_LIST_STYLE)
        # setting list's font
        font = QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        self.history_list.setFont(font)
        # toolbar
        self.tool_bar = QWidget(self)
        self.tool_bar.setStyleSheet(HISTORY_TOOLBUTTON_STYLE)
        self.tool_bar.setMaximumHeight(50)
        # toolbar layout
        self.tool_bar_layout = QHBoxLayout(self.tool_bar)
        #
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Buscar en la caché")
        self.search_input.setClearButtonEnabled(True)
        # tool buttons
        self.search_btn = QToolButton(self)
        self.search_btn.setMaximumSize(30, 30)
        self.search_btn.setMinimumSize(30, 30)
        self.search_btn.setIcon(QIcon(QPixmap(":/icons/icons/search.png")))
        self.search_btn.setIconSize(QSize(25, 25))
        self.search_btn.clicked.connect(lambda: self.load_history(self.search_input.text()))
        #
        self.search_details = QLabel("")
        self.search_details.setStyleSheet("color:white;\nfont: 10pt 'Segou UI';")
        #
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        # #
        self.coogle_img = QLabel("Coogle")
        self.coogle_img.setMaximumSize(70, 40)
        self.coogle_img.setScaledContents(True)
        self.coogle_img.setPixmap(QPixmap(":/logo/designs.png"))
        # self.prev = QToolButton(self)
        # self.prev.setMinimumSize(QSize(25, 25))
        # icon3 = QIcon()
        # icon3.addPixmap(QPixmap(":/rc/graphics/bold_left_arrow.png"), QIcon.Mode.Normal,
        #                 QIcon.State.Off)
        # self.prev.setIcon(icon3)
        # self.prev.setAutoRaise(True)
        # self.prev.setObjectName("prev")
        # #
        # self.next = QToolButton(self)
        # self.next.setMinimumSize(QSize(25, 25))
        # icon4 = QIcon()
        # icon4.addPixmap(QPixmap(":/rc/graphics/bold_right_arrow.png"), QIcon.Mode.Normal,
        #                 QIcon.State.Off)
        # self.next.setIcon(icon4)
        # self.next.setAutoRaise(True)
        # self.next.setObjectName("next")
        # adding to toolbar
        self.tool_bar_layout.addWidget(self.search_input)
        self.tool_bar_layout.addWidget(self.search_btn)
        self.tool_bar_layout.addItem(spacer)
        self.tool_bar_layout.addWidget(self.search_details)
        self.tool_bar_layout.addWidget(self.coogle_img)
        # self.tool_bar_layout.addWidget(self.prev)
        # self.tool_bar_layout.addWidget(self.next)
        # setting tool bar layout
        self.tool_bar.setLayout(self.tool_bar_layout)
        # adding to layout
        self.main_layout.addWidget(self.tool_bar)
        self.main_layout.addWidget(self.history_list)
        # setting dialog's layout
        self.setLayout(self.main_layout)
        # content
        self.history = []
        # put in data
        self.load_history()

    def show_info(self, i):
        element = self.history[i]
        txt = f"Título: {element.criterion}\n\nURL: {element.url}\n\nRespuesta recibida en {element.elapsed_time if element.elapsed_time is not None else '--:--:--'}\nTamaño: {nz(element.size) if element.size is not None else '- Desconocido -'}"
        m = QMessageBox(self)
        m.setIcon(m.Icon.Information)
        m.setWindowTitle("Información")
        m.setText(txt)
        m.setStyleSheet("QLabel{\n"
                        "   color:white;\n"
                        "   font: 12pt 'Segoe UI';\n"
                        "}\n"
                        "QPushButton{\n"
                        "   font: bold 12pt 'Segoe UI';\n"
                        "   color: rgb(255, 255, 255);\n"
                        "   background-color: rgb(0, 209, 255);\n"
                        "   border-radius: 8px;\n"
                        "   padding: 5px;\n"
                        "}\n"
                        "QPushButton: hover{\n"
                        "   background-color: rgb(0, 145, 255);\n"
                        "}\n")
        m.exec_()

    def send_new_request(self, i):
        element = self.history[i]
        self.new_request.emit(element)

    def open_file_response(self):
        i = self.history_list.currentRow()
        element = self.history[i]
        self.open_file.emit(element)

    def load_history(self, search=""):
        self.history = GET_HISTORY(search)
        self.history_list.set_data(self.history)
        #
        if search:
            self.search_details.setText("Encontrados %d resultados"%len(self.history))
        else:
            self.search_details.setText("")
