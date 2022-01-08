from PyQt5.QtCore import QSettings
from util.const import APP_ID
from util.logger import SENT_TO_LOG

DEFAULT_SETTINGS = {"current_user":"",
                    "last_weather_city":"",
                    "last_translator_text":"",
                    "last_web_search_criterion":"",
                    "versicle_traduction":"rvr60",
                    "check_mailbox":"auto",
                    "save_cache":True,
                    "alert_sound":"sound/okay.wav",
                    "show_systray_icon":True}

SETTINGS = QSettings(APP_ID, "settings")
def SAVE_SETTINGS(key, value):
    SETTINGS.setValue(key, value)
    SETTINGS.sync()
try:
    for key in DEFAULT_SETTINGS.keys():
        if SETTINGS.value(key) is None:
            SAVE_SETTINGS(key, DEFAULT_SETTINGS[key])
except Exception as e:
    print("ERROR REESTABLECIENDO CONFIGURACION")
    SENT_TO_LOG(f"REESTABLECIENDO CONFIGURACION {e.args}")