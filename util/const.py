import math
import os
# # ---------------------- APP INFO ----------------------- #
from enum import Enum

def load_file(file):
    try:
        with open(file, "r", encoding="utf-8") as f:
            return f.read()
    except:
        print("No se pudo cargar la hoja de estilos")
def nz(size_bytes):
    if size_bytes == 0:
        return "0.0 B"
    size_name = ("B", "KB", "MB", "GB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])
# APP
VERSION = "1.0"
APP_NAME = "Coogle"
APP_ID = APP_NAME.lower()
AUTHOR = "Javier Alejandro González Casellas"
SUPPORT = "Mi usuario en Telegram: @jalexbeats"
USER_PATH = os.path.expanduser('~')
APP_DATA = os.path.join(USER_PATH, "AppData", "Local", APP_ID)
CACHE = os.path.join(APP_DATA, "cache")
# # --------------------- GRABBER BOT --------------------- #
RUMKIN = "webpage@rumkin.com"
# # --------------------- SMTP CONFIG --------------------- #
SMTP_HOST = "181.225.231.12"
SMTP_PORT = 25
IMAP_HOST = "181.225.231.14"
IMAP_PORT = 143
# # --------------------- WEB -------------------------- #
class SearchEngine(Enum):
    GOOGLE = "http://www.google.com/search?q={}&hl=es&num={}&ie=utf-8&oe=utf-8"
    GOOGLE_IMG = "http://www.google.com/search?q={}&hl=es&ie=utf-8&oe=utf-8&tbm=isch"
    WIKIPEDIA = "https://es.wikipedia.org/wiki/especial:buscar?search={}"
    BING = "https://www.bing.com/search?q={}&setLang=es&count={}"
    YAHOO = ""
class RequestType(Enum):
    HTML = "source"
    TEXT = "url"
    FULL_HTML = "webpage"
    PDF = "pdf"
def get_engine_by_name(name):
    if name == "GOOGLE":
        return SearchEngine.GOOGLE
    elif name == "GOOGLE_IMG":
        return SearchEngine.GOOGLE_IMG
    elif name == "WIKIPEDIA":
        return SearchEngine.WIKIPEDIA
    elif name == "BING":
        return SearchEngine.BING
def get_request_type_by_name(name):
    if name == "HTML":
        return RequestType.HTML
    elif name == "TEXT":
        return RequestType.TEXT
    elif name == "FULL_HTML":
        return RequestType.FULL_HTML
    elif name == "PDF":
        return RequestType.PDF
# ---------------------------------------------------------- #
# # --------------------- WEATHER -------------------------- #
SPECIFIC_WEATHER = "https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&units=metric&appid={}"
WEATHER = "https://api.openweathermap.org/data/2.5/weather?q={}%2Ccu&units=metric&appid=97c22f988bae8824d192d50d5a5410df"
class SkyColor(Enum):
    FORECAST = """QWidget #background{
	background-color: qlineargradient(spread:pad, x1:0.517273, y1:1, x2:0.517, 		y2:0, stop:0 rgba(0, 137, 255, 255), stop:1 rgba(61, 231, 255, 255));
}"""
    GREY = """QWidget #background{
	background-color: qlineargradient(spread:pad, x1:0.500091, y1:1, x2:0.477, y2:0, stop:0 rgba(111, 111, 111, 255), stop:1 rgba(219, 219, 219, 255));
}"""
    NIGHT = """QWidget #background{
background-color: qlineargradient(spread:pad, x1:0.506, y1:0, x2:0.517, y2:1, stop:0 rgba(62, 85, 156, 255), stop:1 rgba(19, 15, 54, 255));
}"""
class LayerType(Enum):
    NONE = ""
    CLEAR = ":/weather/weather_img/sun/sunny_bg_high_light.png"
    CLOUDY = ":/weather/weather_img/layers/clouds.png"#":/weather/weather_img/layers/bg_scrollview_middle_layer_cloudy.png"
    GREY = ":/weather/weather_img/layers/bg_scrollview_middle_layer_grey.png"
    OVERCAST = ":/weather/weather_img/layers/bg_scrollview_middle_layer_overcast.png"
    SANDY = ":/weather/weather_img/layers/bg_scrollview_middle_layer_1200_pad_sandy.png"
    FOG = ":/weather/weather_img/fog/bg_fog_down.png"
import json
MUNICIPALITIES = {"Pinar del Río": ["Consolación del Sur", "Guane", "La Palma", "Los Palacios", "Mantua", "Minas de Matahambre", "Pinar del Río", "San Juan y Martínez", "San Luis", "Sandino", "Viñales"], "Artemisa": ["Alquízar", "Artemisa", "Bauta", "Caimito", "Guanajay", "Güira de Melena", "Mariel", "San Antonio de los Baños", "Bahía Honda", "San Cristóbal", "Candelaria"], "Mayabeque": ["Batabanó", "Bejucal", "Güines", "Jaruco", "Madruga", "Melena del Sur", "Nueva Paz", "Quivicán", "San José de las Lajas", "San Nicolás de Bari", "Santa Cruz del Norte"], "La Habana": ["Arroyo Naranjo", "Boyeros", "Centro Habana", "El Cerro", "Cotorro", "Diez de Octubre", "Guanabacoa", "Habana del Este", "Habana Vieja", "La Lisa", "Marianao", "Playa", "Plaza", "Regla", "San Miguel del Padrón"], "Matanzas": ["Calimete", "Cárdenas", "Ciénaga de Zapata", "Colón", "Jagüey Grande", "Jovellanos", "Limonar", "Los Arabos", "Martí", "Matanzas", "Pedro Betancourt", "Perico", "Unión de Reyes"], "Villa Clara": ["Caibarién", "Camajuaní", "Cifuentes", "Corralillo", "Encrucijada", "Manicaragua", "Placetas", "Quemado de Güines", "Ranchuelo", "Remedios", "Sagua la Grande", "Santa Clara", "Santo Domingo"], "Cienfuegos": ["Abreus", "Aguada de Pasajeros", "Cienfuegos", "Cruces", "Cumanayagua", "Palmira", "Rodas", "Lajas"], "Sancti Spíritus": ["Cabaiguan", "Fomento", "Jatibonico", "La Sierpe", "Sancti Spíritus", "Taguasco", "Trinidad", "Yaguajay"], "Ciego de Ávila": ["Ciro Redondo", "Baraguá", "Bolivia", "Chambas", "Ciego de Ávila", "Florencia", "Majagua", "Morón", "Primero de Enero", "Venezuela"], "Camagüey": ["Camagüey", "Carlos Manuel de Céspedes", "Esmeralda", "Florida", "Guaimaro", "Jimagüayú", "Minas", "Najasa", "Nuevitas", "Santa Cruz del Sur", "Sibanicú", "Sierra de Cubitas", "Vertientes"], "Las Tunas": ["Amancio Rodríguez", "Colombia", "Jesús Menéndez", "Jobabo", "Las Tunas", "Majibacoa", "Manatí", "Puerto Padre"], "Holguín": ["Antilla", "Báguanos", "Banes", "Cacocum", "Calixto García", "Cueto", "Frank País", "Gibara", "Holguín", "Mayarí", "Moa", "Rafael Freyre", "Sagua de Tánamo", "Urbano Noris"], "Granma": ["Bartolomé Masó", "Bayamo", "Buey Arriba", "Campechuela", "Cauto Cristo", "Guisa", "Jiguaní", "Manzanillo", "Media Luna", "Niquero", "Pilón", "Río Cauto", "Yara"], "Santiago de Cuba": ["Contramaestre", "Guamá", "Julio Antonio Mella", "Palma Soriano", "San Luis", "Santiago de Cuba", "Segundo Frente", "Songo la Maya", "Tercer Frente"], "Guantánamo": ["Baracoa", "Caimanera", "El Salvador", "Guantánamo", "Imías", "Maisí", "Manuel Tames", "Niceto Pérez", "San Antonio del Sur", "Yateras"], "Municipo Especial": ["Isla de la Juventud"]}
# ---------------------------------------------------------- #
# # ----------------- TRANSLATOR --------------------------- #
TRANSLATOR = "https://translate.googleapis.com/translate_a/single?client=gtx&sl={}&tl={}&dt=t&q={}"
def lang():
    with open("data/languages_prefix.csv", "r", encoding="utf-8") as csv_file:
        import csv
        plots = tuple(csv.reader(csv_file, delimiter=','))
        if plots:
            lang_list = [(row[0], row[1]) for row in plots[1:]]
            lang_list.insert(0, ("auto", "Detectar idioma"))
            return lang_list
LANGUAGES = []
try:
    LANGUAGES = lang()
except:
    pass
# ---------------------------------------------------------- #
# # --------------- 24H BITCOIN GRAPH ---------------------- #
BITCOIN = "https://www.bitstamp.net/api/v2/ohlc/{}/?step=300&limit=288"
# params -> tipo moneda
# USD -> btcusd
# Libras -> btcgbp
# Eurs -> btceur
class CoinType(Enum):
    USD = "btcusd"
    GBP = "btcgbp"
    EURO = "btceur"
# ---------------------------------------------------------- #
# versiculo
class VersicleType(Enum):
    DAILY = "https://dailyverses.net/get/verse?language={}"
    RANDOM = "https://dailyverses.net/get/random?language={}&isdirect=1&position={}"
# params -> traduccion
class TranslateType(Enum):
    VALERA1960 = "rvr60"
    VALERA1995 = "rvr95"
    NVI = "nvi"
# STYLES
QCOMBOX_STYLE = """QComboBox
{
	font: 12pt "Calibri";
    selection-background-color: #3daee9;
    border-radius:12px;
    border:none;
    padding-left: 10px;
    padding-right: 10px;
    selection-background-color: rgb(62, 62, 62);
    min-width: 75px;
}

QComboBox:drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 12px;
    border:none;
    border-radius:10px;
    background-color: transparent;
}

QComboBox:down-arrow {
    image: url(':/rc/graphics/arrow_down.png');
    height: 12px;
    width: 12px;
    padding-right: 10px;
}

QComboBox:on:hover:focus {
    image: url(':/rc/graphics/arrow_down_disabled.png');
}

QComboBox QAbstractItemView
{
    background-color: #232629;
    border-radius: 10px;
    border: none;
    selection-background-color: #18465d;
    color: rgb(255, 255, 255);
}"""
QMENU_STYLE = """QMenu
{
	background-color: #212121;
	border-radius: 5px;
    color: white;
    margin: 2px;
}

QMenu::icon
{
    margin: 5px;
}

QMenu::item
{
	font: 12pt bold Calibri;
    padding: 5px 30px 5px 30px;
    border-radius: 10px;
	background: transparent;
}

QMenu::item:selected
{
    color: grey;
	background-color: #616161;
}

QMenu::separator {
    height: 2px;
    background: lightblue;
    margin-left: 10px;
    margin-right: 5px;
}

QMenu::indicator {
    width: 18px;
    height: 18px;
}

/* non-exclusive indicator = check box style indicator
   (see QActionGroup::setExclusive) */
QMenu::indicator:non-exclusive:unchecked {
    image: url(:/rc/graphics/checkbox_unchecked.png);
}

QMenu::indicator:non-exclusive:unchecked:selected {
    image: url(:/rc/graphics/checkbox_unchecked_disabled.png);
}

QMenu::indicator:non-exclusive:checked {
    image: url(:/rc/graphics/checkbox_checked.png);
}

QMenu::indicator:non-exclusive:checked:selected {
    image: url(:/rc/graphics/checkbox_checked_disabled.png);
}

/* exclusive indicator = radio button style indicator (see QActionGroup::setExclusive) */
QMenu::indicator:exclusive:unchecked {
    image: url(:/rc/graphics/radio_unchecked.png);
}

QMenu::indicator:exclusive:unchecked:selected {
    image: url(:/rc/graphics/radio_unchecked_disabled.png);
}

QMenu::indicator:exclusive:checked {
    image: url(:/rc/graphics/radio_checked.png);
}

QMenu::indicator:exclusive:checked:selected {
    image: url(:/rc/graphics/radio_checked_disabled.png);
}

QMenu::right-arrow {
    margin: 5px;
    image: url(:/rc/graphics/right_arrow.png)
}"""
HISTORY_TOOLBUTTON_STYLE = """QWidget{
    background-color: black;
}
QToolButton{
	font: 12pt "Segoe UI";
	color: rgb(255, 255, 255);
	/*padding:5px;*/
	border:none;
	border-radius: 10px;
	background-color: transparent;
}

QToolButton:hover{
	background-color: rgb(0, 213, 255);
}
	
QLineEdit{
padding: 5px;
border-radius:10px;
background-color:#8b8b8b;
color:white;
font: 12pt 'Segou UI';
}
QLineEdit:hover{
background-color:#6f6f6f;
}"""
HISTORY_LIST_STYLE = """QWidget{
    background-color:transparent;
}
QListView::item{
	font: 12pt "Segoe UI";
	color: rgb(255, 255, 255);
	/*padding:5px;*/
	border:none;
	border-radius: 10px;
	background-color: transparent;
}
QListWidget{
	background-color: transparent;
	color: rgb(255, 255, 255);
}

QListView::item:!selected:hover {
    background: grey;
	align-content: center;
}

QListView::item:selected:hover{
    background: #287399;
    color: #eff0f1;
}
QAbstractScrollArea
{
    border-radius: 2px;
    /*border: 1px solid #76797C;*/
    background-color: transparent;
    color: white;
}

QScrollBar:horizontal
{
    height: 15px;
    margin: 3px 15px 3px 15px;
    border: 1px transparent #2A2929;
    border-radius: 4px;
    background-color: #2A2929;
}

QScrollBar::handle:horizontal
{
    background-color: #605F5F;
    min-width: 5px;
    border-radius: 4px;
}

QScrollBar::add-line:horizontal
{
    margin: 0px 3px 0px 3px;
    border-image: url(:/rc/graphics/right_arrow_disabled.png);
    width: 10px;
    height: 10px;
    subcontrol-position: right;
    subcontrol-origin: margin;
}

QScrollBar::sub-line:horizontal
{
    margin: 0px 3px 0px 3px;
    border-image: url(:/rc/graphics/left_arrow_disabled.png);
    height: 10px;
    width: 10px;
    subcontrol-position: left;
    subcontrol-origin: margin;
}

QScrollBar::add-line:horizontal:hover,QScrollBar::add-line:horizontal:on
{
    border-image: url(:/rc/graphics/right_arrow.png);
    height: 10px;
    width: 10px;
    subcontrol-position: right;
    subcontrol-origin: margin;
}


QScrollBar::sub-line:horizontal:hover, QScrollBar::sub-line:horizontal:on
{
    border-image: url(:/rc/graphics/left_arrow.png);
    height: 10px;
    width: 10px;
    subcontrol-position: left;
    subcontrol-origin: margin;
}

QScrollBar::up-arrow:horizontal, QScrollBar::down-arrow:horizontal
{
    background: none;
}


QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal
{
    background: none;
}

QScrollBar:vertical
{
    background-color: #2A2929;
    width: 15px;
    margin: 15px 3px 15px 3px;
    border: 1px transparent #2A2929;
    border-radius: 4px;
}

QScrollBar::handle:vertical
{
    background-color: #605F5F;
    min-height: 5px;
    border-radius: 4px;
}

QScrollBar::sub-line:vertical
{
    margin: 3px 0px 3px 0px;
    border-image: url(:/rc/graphics/up_arrow_disabled.png);
    height: 10px;
    width: 10px;
    subcontrol-position: top;
    subcontrol-origin: margin;
}

QScrollBar::add-line:vertical
{
    margin: 3px 0px 3px 0px;
    border-image: url(:/rc/graphics/down_arrow_disabled.png);
    height: 10px;
    width: 10px;
    subcontrol-position: bottom;
    subcontrol-origin: margin;
}

QScrollBar::sub-line:vertical:hover,QScrollBar::sub-line:vertical:on
{

    border-image: url(:/rc/graphics/up_arrow.png);
    height: 10px;
    width: 10px;
    subcontrol-position: top;
    subcontrol-origin: margin;
}


QScrollBar::add-line:vertical:hover, QScrollBar::add-line:vertical:on
{
    border-image: url(:/rc/graphics/down_arrow.png);
    height: 10px;
    width: 10px;
    subcontrol-position: bottom;
    subcontrol-origin: margin;
}

QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical
{
    background: none;
}


QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical
{
    background: none;
}"""

OPEN_WEATHER = {"ID": ["200", "201", "202", "210", "211", "212", "221", "230", "231", "232", "300", "301", "302", "310", "311", "312", "313", "314", "321", "500", "501", "502", "503", "504", "511", "520", "521", "522", "531", "600", "601", "602", "611", "612", "613", "615", "616", "620", "621", "622", "701", "711", "721", "731", "741", "751", "761", "762", "771", "781", "800", "801", "802", "803", "804"], "Main": ["Tormenta", "Tormenta", "Tormenta", "Tormenta", "Tormenta", "Tormenta", "Tormenta", "Tormenta", "Tormenta", "Tormenta", "Llovizna", "Llovizna", "Llovizna", "Llovizna", "Llovizna", "Llovizna", "Llovizna", "Llovizna", "Llovizna", "Lluvia", "Lluvia", "Lluvia", "Lluvia", "Lluvia", "Lluvia", "Lluvia", "Lluvia", "Lluvia", "Lluvia", "Nieve", "Nieve", "Nieve", "Nieve", "Nieve", "Nieve", "Nieve", "Nieve", "Nieve", "Nieve", "Nieve", "Neblina", "Humo", "Neblina", "Polvo", "Niebla", "Arena", "Polvo", "Cenizas", "Ráfaga", "Tornado", "Claro", "Nubes", "Nubes", "Nubes", "Nubes"], "Description": ["Tormenta con lluvia ligera", "Tormenta con lluvia", "Tormenta con lluvia intensa", "Tormenta ligera", "Tormenta", "Tormenta fuerte", "Tormenta irregular", "Tormenta con llovizna ligera", "Tormenta con llovizna", "Tormenta con llovizna intensa", "Llovizna ligera", "Llovizna", "Llovizna de gran intensidad", "Lluvia ligera y llovizna", "Llovizna", "Llovizna intensa", "Lluvia y llovizna", "Lluvia fuerte y llovizna","Llovizna","Lluvia ligera","Lluvia moderada","Lluvia intensa","Lluvia muy intensa","Lluvia extrema", "Lluvia helada","Chubascos de intensidad leve","Chubascos de lluvia","Chubascos de mucha intensidad","Chubascos de lluvia irregulares","nevadas ligeras","nieve","nevadas intensas","aguanieve", "Lluvia ligera de aguanieve", "Lluvia ligera de aguanieve","Lluvia ligera y nieve", "Lluvia y nieve", "Lluvia ligera de nieve", "Lluvia de nieve", "Fuerte lluvia de nieve", "Niebla", "Humo", "Neblina", "Remolinos de arena", "Niebla", "Arena", "Polvo", "Ceniza volcánica", "Borrascas", "Tornado", "Cielo despejado", "Pocas nubes: 11-25%", "Nubes dispersas: 25-50%", "Nubarrón: 51-84%", "Nublado: 85-100%"], "Icon": ["11d", "11d", "11d", "11d", "11d", "11d", "11d", "11d", "11d", "11d", "09d", "09d", "09d", "09d", "09d", "09d", "09d", "09d", "09d", "10d", "10d", "10d", "10d", "10d", "13d", "09d", "09d", "09d", "09d", "13d", "13d", "13d", "13d", "13d", "13d", "13d", "13d", "13d", "13d", "13d", "50d", "50d", "50d", "50d", "50d", "50d", "50d", "50d", "50d", "50d", "01d 01n", "02d 02n", "03d 03n", "04d 04n", "04d 04n"]}