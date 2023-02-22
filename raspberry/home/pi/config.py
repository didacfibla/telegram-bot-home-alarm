# Usuarios autorizados para enviarlos y recibir mensajes (usuario de telegram y un nombre)
knownUsers = {REPLACE_WITH_YOUR_USER_ID: "REPLACE_WITH_YOUR_NAME", REPLACE_WITH_USER_ID2: "REPLACE_WWITH_USER2_NAME"}

# token para la api de telegram
TOKEN = 'REPLACE_WITH_YOUR_BOT_TOKEN'

# ficheros auxiliares (logs y estado de la alarma)
status_file = "/home/pi/bot/status.txt"
log_file = "/home/pi/bot/log.txt"

# Zonas registradas 
zones = {499734: "Puerta casa", # REPLACE WITH THE ID OF YOUR RX DEVICE AND THE NAME OF THE ZONE
         989206: "Balcon" # REPLACE WITH THE ID OF YOUR RX DEVICE AND THE NAME OF THE ZONE
         }
