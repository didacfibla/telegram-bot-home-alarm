# !/usr/bin/env python3

from rpi_rf import RFDevice
import time, telebot, sys, signal, datetime, argparse, logging
from config import status_file
from config import log_file
from config import knownUsers
from config import TOKEN
from config import zones

# CONFIGURACION PARA LOS LOGS


logging.basicConfig(filename=log_file, format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', filemode='a', level=logging.INFO)


# CONFIGURACION DE SEÑALES

def signal_handler(sig, frame):
    logging.info(f"(AlertBot) AlertBot ha finalizado")

    for user in knownUsers.keys():
        bot.send_message(user, "*AlertBot ha finalizado*", parse_mode='Markdown')

    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

# VARIABLES PARA EL BOT

bot = telebot.TeleBot(TOKEN)

# MENSAJE A TODOS CUANDO EL BOT ARRANCA

try:
    for user in knownUsers.keys():
        bot.send_message(user, "📡 *AlertBot se ha iniciado*", parse_mode='Markdown')

    logging.info(f"(AlertBot) AlertBot se ha iniciado")

except:
    logging.info(f"(AlertBot) Ha ocurrido un error al arrancar el bot")

# VARIABLES RECEPTOR RADIOFREQUENCIA

parser = argparse.ArgumentParser(description='Receives a decimal code via a 433MHz GPIO device')
parser.add_argument('-g', dest='gpio', type=int, default=18) # pin 18
args = parser.parse_args()

rfdevice = RFDevice(args.gpio)
rfdevice.enable_rx()


# VARIABLES PARA ALARMA

status = "ARMADO"


def defenseOn():

    timestamp = None

    logging.info(f"(rf433) Modo de defensa activado, escuchando señales en el GPIO {str(args.gpio)}")

    while True:

        hora = datetime.datetime.now().strftime('%H:%M:%S')

        if rfdevice.rx_code_timestamp != timestamp:
            timestamp = rfdevice.rx_code_timestamp
            key = rfdevice.rx_code

            if key in zones.keys():
                logging.info(f"(rf433) Señal recibida de {key}")

                # Si llega una señal de un sensor conocido miramos si el estado es ARMADO
                try:
                    status = open(status_file, "r").read().rstrip()

                except:
                    logging.info(f"(AlertBot) - Error al leer el estado de {status_file}, se asume estado = ARMADO")

                if status == "ARMADO":

                    for user in knownUsers.keys():
                        bot.send_message(user, f"🆘 *ALERTA en {zones[key]} ({hora})*", parse_mode='Markdown')
                        logging.info(f"(AlertBot) ALERTA en {zones[key]}, {knownUsers[user]} ha sido alertado")

                    logging.info(f"(AlertBot) Todos los usuarios ({knownUsers.values()}) han sido alertados de la incidencia en {zones[key]}")
                    time.sleep(6)

        time.sleep(0.1)

    rfdevice.cleanup()


if __name__ == "__main__":
    defenseOn()
