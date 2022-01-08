import sys
from enum import Enum

from PyQt5 import QtCore
from PyQt5.QtCore import QPropertyAnimation, Qt, pyqtProperty
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel

class AnimType(Enum):
    RECEIVED_WEATHER = [f":/animation_weather_ok/weather_img/refresh_anim/refresh_cloud_shape_{i}.png" for i in range(16)]
    INTRO = [f":/intro_animation/weather_img/intro_anim/ani{i}.png" for i in range(10, 27)]

# import os
# print(os.path.exists("../:/weather/weather_img/refresh_anim/" + RECEIVED_WEATHER[0]))

class SeqAnimatedLabel(QLabel):
    def __init__(self, parent=None, pixmap="", anim_type=AnimType.INTRO):
        QLabel.__init__(self)
        self.parent = parent
        #
        self.anim_type = anim_type
        #
        self._frame = 0
        # animation
        self.loop_count = 2
        self.duration = 2000
        self.animation = QPropertyAnimation(self, b"frame")
        self.animation.setDuration(self.duration)
        self.animation.setStartValue(0)
        self.animation.setEndValue(15)
        self.animation.setLoopCount(self.loop_count)
        # pixmap
        self.pixmap = None
        self.set_pixmap(pixmap)
        #
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setMaximumHeight(30)
        self.setMinimumWidth(30)
        self.setScaledContents(True)

    def set_animation_type(self, anim:AnimType):
        self.anim_type = anim
        if self.anim_type == AnimType.RECEIVED_WEATHER:
            self.loop_count = 1
            self.duration = 1000

    def set_pixmap(self, pixmap, to_animate=False):
        if not to_animate:
            self.stop_animation()
        self.pixmap = QPixmap(pixmap)
        self.pixmap = self.pixmap.scaled(self.size(), Qt.IgnoreAspectRatio)
        self.setPixmap(self.pixmap)

    def start_animation(self):
        #if self.animation.state() != QtCore.QAbstractAnimation.Running:
        self.animation.start()

    def stop_animation(self):
        #if self.animation.state() == QtCore.QAbstractAnimation.Running:
        self.animation.stop()
        self.frame = 0

    @pyqtProperty(int)
    def frame(self):
        return self._frame

    @frame.setter
    def frame(self, value):
        self._frame = value
        self.set_pixmap(self.anim_type.value[self._frame], to_animate=True)
        if self._frame == 15:
            self.parent.setVisible(False)
# >---------------------------------------------------------------------------------------------------------------------<

# class Prueba(QDialog):
#     def __init__(self):
#         QDialog.__init__(self)
#         self.setStyleSheet("background-color:grey")
#         self.setObjectName("Dialog")
#         self.resize(100, 150)
#         self.gridLayout = QGridLayout(self)
#         self.gridLayout.setObjectName("gridLayout_2")
#         self.spinner = SeqAnimatedLabel(parent=self, pixmap=":/weather/weather_img/refresh_anim/" + RECEIVED_WEATHER[0])
#         #self.spinner.setPixmap(QPixmap("imgLoadingLarge.png"))
#         self.spinner.setScaledContents(True)
#         self.spinner.setMinimumSize(50, 50)
#         self.gridLayout.addWidget(self.spinner)
#         self.button = QPushButton("Fuegooooo")
#         self.gridLayout.addWidget(self.button)
#         self.button.clicked.connect(self.spinner.start_animation)
#         self.show()
#
# def main():
#     app = QApplication(sys.argv)
#     window = Prueba()
#     window.show()
#     app.exec()
#
# if __name__ == '__main__':
#     main()