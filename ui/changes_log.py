from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QDialog, QTextEdit, QVBoxLayout

CHANGES = """Coogle - Historial de cambios
=============================
v1.0
- Implementada la funcionalidad de consultar el clima para cualquier región del mundo. Con autocompletamiento para las ciudades de Cuba.
- Implementada la funcionalidad que permite realizar traducciones con Google Translator.
	+ 248 idiomas disponibles para traducir
- Implementada la funcionalidad  para solicitar versículo de la biblia diario o cualquiera al azar.
	+ Agregada opción para seleccionar el formato de traducción del versículo
	+ Agregada opción para guardar versículo o agregarlo al portapapeles
- Implementada la funcionalidad para navegar por Internet.
	+ Agregado motores de búsquedas Google, Google Images, Wikipedia, Bing
	+ Agregada opción de formato de respuesta (solo HTML, HTML completa, etc.)
	+ Agregada opción para mostrar por cantidad de resultados
	+ Agregado sistema de caché
	+ Agregado sistema de Historial de búsquedas
	+ Agregada pestaña principal Coogle de navegación
- Implementado sistema de Preferencias
	+ Agregado sistema de Autenticación de usuario
 """
import ui.resources
class ChangesLOG(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setWindowTitle("Historial de cambios")
        self.setWindowIcon(QIcon(":/logo/logo.png"))
        self.setFixedSize(800, 500)
        self.layout = QVBoxLayout(self)
        self.text = QTextEdit(self)
        font = QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(16)
        self.text.setFont(font)
        self.text.setReadOnly(True)
        self.text.setPlainText(CHANGES)
        self.layout.addWidget(self.text)
        self.setLayout(self.layout)
        self.setModal(True)