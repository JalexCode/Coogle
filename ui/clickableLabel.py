from PyQt5.QtCore import QTimer, pyqtSignal, Qt
from PyQt5.QtWidgets import QApplication, QLabel

NORMAL_STYLE = """color:rgba(255, 255, 255, 150);
font: 24pt 'Segoe UI';
background-color:rgba(0, 0, 0, 100);"""
LINK_STYLE = """color: rgba(20, 216, 255, 100);
font: 24pt 'Segoe UI';
background-color:rgba(0, 0, 0, 100);"""
# color: rgba(20, 216, 255, 100);
# border-radius:20px;
# padding:10px;"""

class QLabelClickable(QLabel):
    clicked = pyqtSignal(str)
    def __init__(self, parent=None):
        super(QLabelClickable, self).__init__(parent)
        self.setStyleSheet(NORMAL_STYLE)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def enterEvent(self, event):
        self.setStyleSheet(LINK_STYLE)

    def leaveEvent(self, event):
        self.setStyleSheet(NORMAL_STYLE)

    def mousePressEvent(self, event):
        self.ultimo = "Clic"

    def mouseReleaseEvent(self, event):
        if self.ultimo == "Clic":
            QTimer.singleShot(QApplication.instance().doubleClickInterval(),
                              self.performSingleClickAction)
        else:
            # Realizar acción de doble clic.
            self.clicked.emit(self.ultimo)

    def mouseDoubleClickEvent(self, event):
        self.ultimo = "Doble Clic"

    def performSingleClickAction(self):
        if self.ultimo == "Clic":
            self.clicked.emit(self.ultimo)