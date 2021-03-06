from PyQt5 import uic

def ui2py(name:str):
    with open(f"{name}.ui", "r") as ui:
        with open(f"{name}.py", "w") as py:
            uic.compileUi(ui, py, True)
def change_somethings(name:str, replace:dict):
    content = ""
    with open(f"{name}.py", "r", encoding="UTF-8") as py:
        content = py.read()
    with open(f"{name}.py", "w", encoding="UTF-8") as py:
        for key in replace:
            try:
                if not key.startswith("#A#"):
                    content = content.replace(key, replace[key])
                else:
                    to_add = key.replace("#A#", "")
                    splitted = content.split(to_add)
                    idx = splitted.index(to_add)
                    splitted.insert(idx+1, replace[key])
                    content = "".join(splitted)
            except Exception as e:
                print(e.args)
        py.write(content)

ui2py("main")
dict = {"import qss_icons_rc":"import ui.resources",
        ":/qss_icons/rc":":/rc/graphics",
        "QtGui.QIcon.Normal, QtGui.QIcon.Off":"QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off",
        "QtCore.Qt.AlignCenter":"QtCore.Qt.AlignmentFlag.AlignCenter",
        "QtCore.Qt.AlignHCenter":"QtCore.Qt.AlignmentFlag.AlignHCenter",
        "QtCore.Qt.AlignVCenter":"QtCore.Qt.AlignmentFlag.AlignVCenter",
        "QtCore.Qt.AlignRight":"QtCore.Qt.AlignmentFlag.AlignRight",
        "QtCore.Qt.AlignTrailing":"QtCore.Qt.AlignmentFlag.AlignTrailing",
        "QtCore.Qt.PlainText": "QtCore.Qt.TextFormat.PlainText"}
change_somethings("main", dict)
#
ui2py("settings")
change_somethings("settings", dict)