from flask import Flask, request, jsonify
import requests
from webexteamssdk import WebexTeamsAPI

# Configuración de Flask
app = Flask(__name__)

# Tokens de acceso
WEBEX_BOT_TOKEN = 'NDI1MzQ5MmItOGMxNi00MTA3LTlhYzEtNWNjZjI3OTllOGNkMDU3MzljYTctYzk0_PF84_a91d9855-d761-4b0a-a9e5-7d2345410a6d'
PERSONAL_ACCESS_TOKEN = 'NzlhMmFjNjMtOTMzMC00NGZjLTg2NzEtN2QyMzI5ZWVmYTljMzNkMzI2M2UtZWY5_PF84_a91d9855-d761-4b0a-a9e5-7d2345410a6d'

# Nueva URL de Webex para obtener licencias
LICENSES_URL = 'https://webexapis.com/v1/licenses'

# Inicializar la API de Webex Teams
api = WebexTeamsAPI(access_token=WEBEX_BOT_TOKEN)

# Función para obtener el estado de las licencias
def obtener_estado_licencias():
    headers = {
        'Authorization': f'Bearer {PERSONAL_ACCESS_TOKEN}',  # Usamos el token personal
        'Content-Type': 'application/json'
    }

    print("Solicitando estado de licencias...")  # Log de depuración
    response = requests.get(LICENSES_URL, headers=headers)

    if response.status_code == 200:
        data = response.json()

        if 'items' in data:
            licencias = data['items']
            if len(licencias) == 0:
                return "No hay licencias registradas."

            resultado = []
            for licencia in licencias:
                nombre = licencia.get('name', 'Desconocido')
                cantidad_total = licencia.get('totalUnits', 'Desconocido')
                cantidad_en_uso = licencia.get('consumedUnits', 'Desconocido')
                resultado.append(f"Licencia: {nombre}\n  - Total: {cantidad_total}\n  - En uso: {cantidad_en_uso}")

            return "\n".join(resultado)
        else:
            return "No se encontraron licencias en la respuesta."

    else:
        return f"Error al obtener el estado de las licencias: {response.status_code}, {response.text}"

# Función para manejar los mensajes del bot
def handle_message(message, room_id):
    print(f"Recibido mensaje: {message.text}")  # Log de depuración
    if message.text:
        if 'estado de licencias' in message.text.lower():
            estado_licencias = obtener_estado_licencias()
            response = f"📋 Estado de las licencias:\n\n{estado_licencias}"
        else:
            response = "🤖 No entendí tu solicitud. Puedes preguntar por 'estado de licencias'."
        
        print(f"Enviando respuesta: {response}")  # Log de depuración
        api.messages.create(roomId=room_id, text=response)

# Función para escuchar los mensajes en Webex Teams
def listen_for_messages():
    rooms = api.rooms.list()
    if not rooms:
        print("El bot no está en ningún espacio.")
        return
    
    room_id = rooms[0].id  # Tomamos el primer roomId encontrado
    print(f"Escuchando mensajes en el roomId: {room_id}")  # Log de depuración

    messages = api.messages.list(roomId=room_id)
    for message in messages:
        handle_message(message, room_id)

# Ruta Webhook (Render la usará)
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Datos recibidos del Webhook:", data)  # Log para ver los datos recibidos
    if 'data' in data:
        message_id = data['data']['id']
        manejar_mensaje(message_id)
    return "OK", 200

# Función para procesar el mensaje recibido en el Webhook
def manejar_mensaje(message_id):
    headers = {
        'Authorization': f'Bearer {WEBEX_BOT_TOKEN}',
        'Content-Type': 'application/json'
    }

    # Obtener detalles del mensaje
    response = requests.get(f'https://webexapis.com/v1/messages/{message_id}', headers=headers)
    if response.status_code == 200:
        message_data = response.json()
        message_text = message_data.get('text', '').lower()
        room_id = message_data.get('roomId')

        # Verifica si el mensaje es "estado de licencias"
        if "estado de licencias" in message_text:
            estado = obtener_estado_licencias()
            api.messages.create(roomId=room_id, text=f"📋 Estado de las licencias:\n\n{estado}")

# Ejecutar la aplicación Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



