from threading import Thread

from util.logger import SENT_TO_LOG, SHOW_CONSOLE_LOG


class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._target = target
        self.return_value = None

    def run(self):
        #try:
        if self._target is not None:
            self.return_value = self._target(*self._args, **self._kwargs)
            #self.setDaemon(True)
        #except Exception as e:
            #SENT_TO_LOG(f"Fallo en funcion {self._target.__name__} {e.args}")
            #SHOW_CONSOLE_LOG("Error", f"[Hilo] Fallo en funcion {self._target.__name__} {e.args}")

    def join(self, *args):
        Thread.join(self, *args)
        return self.return_value