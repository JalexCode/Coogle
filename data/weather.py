from datetime import time, datetime

from imap_tools import MailBoxUnencrypted

from util.const import IMAP_HOST, IMAP_PORT, LayerType, SkyColor, MUNICIPALITIES, WEATHER, OPEN_WEATHER
from util.logger import SHOW_CONSOLE_LOG, SENT_TO_LOG
from data.service import Service

IMG_REDIRECT = {"01d":'daily_forecast_sunny.png', "02d":'daily_forecast_cloudy.png',
                "03d":'daily_forecast_overcast.png', "04d":'cloudy.png', "09d":'daily_forecast_moderate_rain.png',
                "10d":'daily_forecast_heavy_rain.png', "11d":'daily_forecast_t_storm.png',
                "13d":'daily_forecast_heavy_snow.png', "50d":'daily_forecast_foggy.png',
                "01n":'daily_forecast_sunny_night.png', "02n":'daily_forecast_cloudy_night.png',
                "03n":'icon_gray_bg_overcast.png', "04n":'cloudy.png', "09n":'icon_gray_bg_moderate_rain.png',
                "10n":'icon_gray_bg_heavy_rain', "11n":'icon_gray_bg_t_storm.png',
                "13n":'icon_gray_bg_heavy_snow.png', "50n":'icon_gray_bg_fog.png'}

class Weather(Service):
    def __init__(self, user: str, passw: str, criterion: str):
        Service.__init__(self, user, passw, criterion)
        # setup Mime text
        self.setup_mime_text()
        # temperatura
        self.temp = 0
        self.max_temp = 0
        self.min_temp = 0
        self.feels_like = 0
        # clima
        self.weather = ""
        # icono
        self.icon = ""
        # viento
        self.wind = 0
        # presion
        self.pressure = 0
        # humedad
        self.humidity = 0
        # pais
        self.country = ""
        # coordenadas
        self.long = 0
        self.lat = 0
        # nivel del mar
        self.sea_lvl = 0
        # nivel del suelo
        self.ground_lvl = 0
        # amanecer
        self.sunrise = time(0, 0, 0)
        # anochecer
        self.sunset = time(0, 0, 0)
        # fecha de actualizacion
        self.datetime = datetime.now()
        # tipo de nubes
        self.clouds_layer = LayerType.CLEAR
        # color del cielo
        self.sky_color = SkyColor.FORECAST

    def setup_subject(self):
        weather_to_format = WEATHER
        if self.criterion not in MUNICIPALITIES:
            weather_to_format = weather_to_format.replace("%2Ccu", "")
        criterion = self.encoding_criterion(True)[1]
        SHOW_CONSOLE_LOG("2.0.2", "Construyendo URL para Google Weather", 2)
        criterion = weather_to_format.format(criterion)
        # Asunto del mensaje
        subject = f"source {criterion}"
        self._message['Subject'] = subject
        SHOW_CONSOLE_LOG("INFO", f"Asunto creado!", 2)
        SHOW_CONSOLE_LOG("INFO", f"Cuerpo del mensaje:", 2)
        print(self._message)

    def receive_data(self):
        try:
            SHOW_CONSOLE_LOG("INFO", "Pagina Web", 1)
            MailMessage = Service.receive_data(self)
            if MailMessage:
                SHOW_CONSOLE_LOG("5.1.1", "Descargando texto...", 1)
                # coger contenido
                #io.StringIO(MailMessage.text)
                unparsed = MailMessage.text
                SHOW_CONSOLE_LOG("INFO", "TEXTO DESCARGADO!", 2)
                #
                SHOW_CONSOLE_LOG("5.1.2", "Eliminando el mensaje del servidor", 1)
                try:
                    with MailBoxUnencrypted(IMAP_HOST, IMAP_PORT).login(self._user, self._passw) as imap:
                        imap.delete(MailMessage.uid)
                        SHOW_CONSOLE_LOG("INFO", "Archivo eliminado!", 2)
                except Exception as e:
                    SENT_TO_LOG(f"Iniciando servidor IMAP {e.args}")
                    SHOW_CONSOLE_LOG("Error", f"Iniciando servidor IMAP{e.args}")
                #
                SHOW_CONSOLE_LOG("INFO", "Cerrando sesion", 1)
                #
                self.parse_response(unparsed)
        except Exception as e:
            SENT_TO_LOG(f"Recibiendo archivo WEB{e.args}")
            SHOW_CONSOLE_LOG("Error", f"Recibiendo archivo WEB{e.args}")

    def parse_response(self, unparsed:str):
        try:
            if unparsed:
                print("Recibido: ", unparsed)
                SHOW_CONSOLE_LOG("5.2", "Parseando respuesta")
                if "error" in unparsed.lower():
                    raise Exception(f"No hay resultados para '{self.criterion}'")
                import json
                dict = json.loads(unparsed)
                print(dict)
                #
                weather_json = OPEN_WEATHER
                # clima
                w = dict["weather"][0]
                id = w["id"]
                idx = weather_json["ID"].index(str(id))
                main = weather_json["Main"][idx]
                self.weather = weather_json["Description"][idx]
                #
                icon = IMG_REDIRECT[w["icon"]]
                self.icon = ":/weather/weather_img/img/" + icon
                # color del cielo y nubes
                self.clouds_layer = LayerType.CLEAR
                if "d" in w["icon"]:
                    self.sky_color = SkyColor.FORECAST
                elif "n" in w["icon"]:
                    self.sky_color = SkyColor.NIGHT
                if main in ["Lluvia", "Tormenta", "Tornado"]:
                    self.sky_color = SkyColor.GREY
                    self.clouds_layer = LayerType.GREY
                if main in ["Nubes", "Nieve", "Llovizna"]:
                    self.clouds_layer = LayerType.CLOUDY
                elif main in ["Arena", "Polvo"]:
                    self.clouds_layer = LayerType.SANDY
                elif main in ["Niebla", "Neblina"]:
                    self.clouds_layer = LayerType.FOG
                # details
                self.temp = dict["main"]["temp"]
                self.feels_like = dict["main"]["feels_like"]
                self.max_temp = dict["main"]["temp_max"]
                self.min_temp = dict["main"]["temp_min"]
                #
                self.pressure = dict["main"]["pressure"]
                self.humidity = dict["main"]["humidity"]
                try:
                    self.sea_lvl = dict["main"]["sea_level"]
                except:
                    pass
                try:
                    self.ground_lvl = dict["main"]["grnd_level"]
                except:
                    pass
                #
                self.wind = dict["wind"]["speed"]
                #
                self.datetime = datetime.fromtimestamp(dict["dt"])
                #
                self.country = dict["sys"]["country"]
                with open("data/countries_data.csv", "r", encoding="utf-8") as csv_file:
                    import csv
                    plots = tuple(csv.reader(csv_file, delimiter=','))
                    if plots:
                        for rows in plots:
                            if rows[3] == self.country:
                                self.country = rows[0]
                                break
                #
                self.sunrise = datetime.fromtimestamp(dict["sys"]["sunrise"])
                self.sunset = datetime.fromtimestamp(dict["sys"]["sunset"])
                # coordenadas
                self.long = dict["coord"]["lon"]
                self.lat = dict["coord"]["lat"]
                # signal
                self.finish_signal.emit(self)
        except Exception as e:
            self.error_signal.emit("Parseando datos del clima", e.args)
