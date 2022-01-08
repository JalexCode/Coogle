import sys

from PyQt5 import uic

with open("main.ui", "r") as ui:
    with open("main.py", "w") as py:
        a = uic.compileUi(ui, py, True)