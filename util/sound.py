# >---------------------------------------------------------------------------------------------------------------------<
import os
import threading

#import pyaudio
#import wave

from PyQt5.QtCore import QObject, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QSound

chunk = 1024


class ReproducirSonido(QObject):
    # alertar = pyqtSignal()
    def __init__(self, parent=None):
        super(ReproducirSonido, self).__init__(parent)

    def run(self, sonido_dir):
        # ABRIMOS UBICACIÓN DEL AUDIO.
        # f = wave.open(sonido_dir, "rb")
        #
        # # INICIAMOS PyAudio.
        # p = pyaudio.PyAudio()
        #
        # # ABRIMOS STREAM
        # stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
        #                 channels=f.getnchannels(),
        #                 rate=f.getframerate(),
        #                 output=True)
        #
        # # LEEMOS INFORMACIÓN
        # data = f.readframes(chunk)
        #
        # # REPRODUCIMOS "stream"
        # while data:
        #     stream.write(data)
        #     data = f.readframes(chunk)
        #
        # # PARAMOS "stream".
        # stream.stop_stream()
        # stream.close()
        #
        # # FINALIZAMOS PyAudio
        # p.terminate()
        QSound.play(r"sound\okay.wav")
        #print("Falta PyAudio y Waves")

def play_audio(dir):
    if os.path.exists(dir):
        sonido_thread = ReproducirSonido()
        thread = threading.Thread(target=sonido_thread.run, args=(dir,))
        thread.start()