from flask import Flask, request, jsonify
import requests
from webexteamssdk import WebexTeamsAPI

app = Flask(__name__)

# Configuración del bot
WEBEX_BOT_TOKEN = 'TU_WEBEX_BOT_TOKEN'
WEBEX_API_URL = 'https://webexapis.com/v1/messages'

api = WebexTeamsAPI(access_token=WEBEX_BOT_TOKEN)

# Ruta Webhook (Render la usará)
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if 'data' in data:
        message_id = data['data']['id']
        manejar_mensaje(message_id)
    return "OK", 200

# Función para procesar el mensaje recibido
def manejar_mensaje(message_id):
    headers = {
        'Authorization': f'Bearer {WEBEX_BOT_TOKEN}',
        'Content-Type': 'application/json'
    }

    # Obtener detalles del mensaje
    response = requests.get(f"{WEBEX_API_URL}/{message_id}", headers=headers)
    if response.status_code == 200:
        message_data = response.json()
        message_text = message_data.get('text', '').lower()
        room_id = message_data.get('roomId')

        # Verifica si el mensaje es "estado de licencias"
        if "estado de licencias" in message_text:
            estado = obtener_estado_licencias()
            api.messages.create(roomId=room_id, text=f"📋 Estado de las licencias:\n\n{estado}")

# Función para obtener las licencias desde Webex
def obtener_estado_licencias():
    headers = {'Authorization': f'Bearer {WEBEX_BOT_TOKEN}', 'Content-Type': 'application/json'}
    response = requests.get('https://webexapis.com/v1/licenses', headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if 'items' in data:
            licencias = [f"{lic['name']}: {lic['consumedUnits']} en uso de {lic['totalUnits']}" for lic in data['items']]
            return "\n".join(licencias)
    
    return "Error al obtener licencias."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


