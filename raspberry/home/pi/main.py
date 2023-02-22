# ESTE PROGRAMA SE ENCARGA DE EJECUTAR LOS 2 BOTS
import signal
import sys
import time
import subprocess

from os.path import exists
from config import log_file
from config import status_file


def signal_handler(sig, frame):
    bot1.send_signal(signal.SIGINT)
    bot2.send_signal(signal.SIGINT)
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    time.sleep(20)
    # Nos aseguramos que el fichero de estado y el fichero de log existan y si no, los creamos
    if not exists(log_file):
        log = open(log_file, "a")

    # Estado por defecto al arrancar: ARMADO
    estado = open(status_file, "w")
    estado.write("ARMADO")
    estado.flush()

    bot1 = subprocess.Popen(["python3", "/home/pi/bot/alertBot.py"], shell=False)
    time.sleep(2)
    bot2 = subprocess.Popen(["python3", "/home/pi/bot/pollingBot.py"], shell=False)

    while True:
        time.sleep(1)
