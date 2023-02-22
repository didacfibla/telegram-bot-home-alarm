# Tutorial initial setup: https://www.flopy.es/crea-un-bot-de-telegram-para-tu-raspberry-ordenale-cosas-y-habla-con-ella-a-distancia/
# API Documentation: https://github.com/eternnoir/pyTelegramBotAPI

import logging, time, telebot, os, sys, signal, requests
import subprocess
from telebot import types

# VARIABLES GLOBALES

from config import status_file
from config import log_file
from config import knownUsers
from config import TOKEN

# CONFIGURACION PARA LOS LOGS

logging.basicConfig(filename=log_file, format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', filemode='a', level=logging.INFO)


# CONFIGURACION DE SEÑALES

def signal_handler(sig, frame):
    logging.info(f"(PollingBot) PollingBot ha finalizado")

    for user in knownUsers.keys():
        bot.send_message(user, "*PollingBot ha finalizado*", parse_mode='Markdown')

    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

# VARIABLES PARA EL BOT

markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True, one_time_keyboard=False)
bot = telebot.TeleBot(TOKEN)
bot.state = None
COMMAND = 1


commands = {"/estado": "Muestra el estado actual del sistema",
            "/armar": "Arma el sistema",
            "/desarmar": "Desarma el sistema",
            "/puerta": "Abrir puerta calle"
            }

commandsHelp = {"/start": "Inicia el chat con el bot",
                "/help": "Muestra todos los comandos disponibles",
                "/bash": "Ejecuta un comando a nivel de sistema",
                "/estado": "Muestra el estado actual del sistema",
                "/armar": "Arma el sistema",
                "/desarmar": "Desarma el sistema",
                "/puerta": "Abre la puerta de la calle"
                }

# MENSAJE A TODOS CUANDO EL BOT ARRANCA

for user in knownUsers.keys():
    bot.send_message(user, "*PollingBot se ha iniciado*", parse_mode='Markdown')

logging.info(f"(PollingBot) PollingBot se ha iniciado")


def generate_buttons(bts_names, markup):
    for button in bts_names:
        markup.add(types.KeyboardButton(button))

    return markup


@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id in knownUsers.keys():

        logging.info(f"(PollingBot) PollingBot da la bienvenida a {knownUsers[message.chat.id]}")

        bot.send_message(message.chat.id, "*¡PollingBot te da la bienvenida!*", parse_mode='Markdown')
        bot.send_message(message.chat.id, "*Que desear hacer?*", reply_markup=markup, parse_mode='Markdown')

    else:
        bot.send_message(message.chat.id, "*Usuario no autorizado*", parse_mode='Markdown')
        logging.info(f"(PollingBot) Usuario no autorizado ({message.chat.id}) ha solicitado /start")


@bot.message_handler(commands=['help'])
def help(message):
    if message.chat.id in knownUsers.keys():

        logging.info(f"(PollingBot) {knownUsers[message.chat.id]} ha solicitado /help")
        text = ""

        for elem in commandsHelp.keys():
            text += elem + ": " + commandsHelp[elem] + "\n\n"

        bot.send_message(message.chat.id, "ℹ *Información de los comandos que puedes ejecutar*\n\n" + text, reply_markup=markup, parse_mode='Markdown')
        bot.send_message(message.chat.id, "*Que desear hacer?*", reply_markup=markup, parse_mode='Markdown')

    else:
        logging.info(f"(PollingBot) Usuario no autorizado ({message.chat.id}) ha solicitado /ayuda")
        bot.send_message(message.chat.id, "*Usuario no autorizado*", parse_mode='Markdown')


@bot.message_handler(commands=['bash'])
def execute_command(message):
    if message.chat.id in knownUsers.keys():

        logging.info(f"(PollingBot) {knownUsers[message.chat.id]} ha solicitado /bash")

        bot.send_message(message.chat.id, "💻 *Ejecución de un comando a nivel de sistema*\n"
                                          "Introduce el comando bash que deseas ejecutar: ", parse_mode='Markdown')
        bot.state = COMMAND

    else:
        logging.info(f"(PollingBot) Usuario no autorizado ({message.chat.id}) ha solicitado /ayuda")
        bot.send_message(message.chat.id, "*Usuario no autorizado*", parse_mode='Markdown')


@bot.message_handler(commands=['estado'])
def status(message):
    if message.chat.id in knownUsers.keys():

        logging.info(f"(PollingBot) {knownUsers[message.chat.id]} ha solicitado /estado")

        try:
            estado_alarma = open(status_file, "r").readline().rstrip()
        except:
            open(status_file, "w").write("ARMADO")
            estado_alarma = open(status_file, "r").readline().rstrip()

        try:
            temperatura = str(subprocess.run(['cat', '/sys/class/thermal/thermal_zone0/temp'], stdout=subprocess.PIPE).stdout)[2:4]
        except:
            temperatura = "❓"

        try:
            disk = str(subprocess.run(['df', '-h', '/'], stdout=subprocess.PIPE).stdout)[80:84]
        except:
            disk = "❓"

        bot.send_message(message.chat.id, f"📊 *Resumen del estado del sistema*\n\n"
                                          f"*🛡 Estado:* {estado_alarma}\n"
                                          f"*🌡 Temperatura:* {temperatura}\n"
                                          f"*💾 Espacio disco:* {disk}", parse_mode='Markdown')

    else:
        logging.info(f"(PollingBot) Usuario no autorizado ({message.chat.id}) ha solicitado /estado")
        bot.send_message(message.chat.id, "*Usuario no autorizado*", parse_mode='Markdown')


@bot.message_handler(func=lambda msg: bot.state == COMMAND)
def exec(message):
    if message.chat.id in knownUsers.keys():

        logging.info(f"(PollingBot) {knownUsers[message.chat.id]} ha solicitado ejecutar: {message.text}")

        f = os.popen(message.text)
        result = f.read()
        bot.send_message(message.chat.id, "Resultado: \n\n" + result)

        bot.state = None
        bot.send_message(message.chat.id, "*\n\nQue desear hacer?*", reply_markup=markup, parse_mode='Markdown')

    else:
        logging.info(f"(PollingBot) Usuario no autorizado ({message.chat.id}) ha solicitado ejectuar {message.text}")
        bot.send_message(message.chat.id, "*Usuario no autorizado*", parse_mode='Markdown')


@bot.message_handler(commands=['armar'])
def armar(message):
    if message.chat.id in knownUsers.keys():

        logging.info(f"(PollingBot) {knownUsers[message.chat.id]} ha solicitado armar el sistema")

        try:
            open(status_file, "w").write("ARMADO")
            estado_alarma = open(status_file, "r").readline().rstrip()
        except:
            estado_alarma = "ARMADO"

        bot.send_message(message.chat.id, f"*🔐 SISTEMA {estado_alarma}* 🔐", parse_mode='Markdown')

    else:
        logging.info(f"(PollingBot) Usuario no autorizado ({message.chat.id}) ha solicitado armar el sistema")
        bot.send_message(message.chat.id, "*Usuario no autorizado*", parse_mode='Markdown')


@bot.message_handler(commands=['desarmar'])
def desarmar(message):
    if message.chat.id in knownUsers.keys():

        logging.info(f"(PollingBot) {knownUsers[message.chat.id]} ha solicitado desarmar el sistema")

        try:
            open(status_file, "w").write("DESARMADO")
            estado_alarma = open(status_file, "r").readline().rstrip()
        except:
            estado_alarma = "DESARMADO"

        bot.send_message(message.chat.id, f"*🔓 SISTEMA {estado_alarma} 🔓*", parse_mode='Markdown')

    else:
        logging.info(f"(PollingBot) Usuario no autorizado ({message.chat.id}) ha solicitado desarmar el sistema")
        bot.send_message(message.chat.id, "*Usuario no autorizado*", parse_mode='Markdown')



@bot.message_handler(commands=['puerta'])
def puerta(message):
    if message.chat.id in knownUsers.keys():

        logging.info(f"(PollingBot) {knownUsers[message.chat.id]} ha solicitado abrir la puerta")

        try:
            value = requests.get('http://192.168.1.200/abrir')

            if value.status_code == 200:
                 bot.send_message(message.chat.id, f"*🚪PUERTA ABIERTA*", parse_mode='Markdown')
            else:
                 bot.send_message(message.chat.id, f"*🚪Algo ha ido mal ...*", parse_mode='Markdown')

        except Exception as e:
            logging.info(f"Ha ocurrido un error al abrir la puerta: {e}")

    else:
        logging.info(f"(PollingBot) Usuario no autorizado ({message.chat.id}) ha solicitado abrir la puerta")
        bot.send_message(message.chat.id, "*Usuario no autorizado*", parse_mode='Markdown')



@bot.message_handler(func=lambda message: True)
def command_default(message):
    if message.chat.id in knownUsers.keys():

        logging.info(f"(PollingBot) {knownUsers[message.chat.id]} ha escrito: {message.text}")

        if message.text not in commandsHelp.keys():
            bot.send_message(message.chat.id, "No te entiendo, prueba con /help")

    else:
        logging.info(f"(PollingBot) Usuario no autorizado ({message.chat.id}) ha solicitado: {message.chat}")


if __name__ == "__main__":

    markup = generate_buttons(commands.keys(), markup)
    bot.infinity_polling()
