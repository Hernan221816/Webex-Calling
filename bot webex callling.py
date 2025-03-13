import requests
from webexteamssdk import WebexTeamsAPI
import time

# Tokens de acceso
WEBEX_BOT_TOKEN = 'NDI1MzQ5MmItOGMxNi00MTA3LTlhYzEtNWNjZjI3OTllOGNkMDU3MzljYTctYzk0_PF84_a91d9855-d761-4b0a-a9e5-7d2345410a6d'
PERSONAL_ACCESS_TOKEN = 'NzlhMmFjNjMtOTMzMC00NGZjLTg2NzEtN2QyMzI5ZWVmYTljMzNkMzI2M2UtZWY5_PF84_a91d9855-d761-4b0a-a9e5-7d2345410a6d'

# URL de Webex Control Hub para obtener el estado de licencias
LICENSES_URL = 'https://webexapis.com/v1/licenses'

# Inicializar la API de Webex Teams
api = WebexTeamsAPI(access_token=WEBEX_BOT_TOKEN)

# Función para obtener el estado de las licencias desde Webex Control Hub
def obtener_estado_licencias():
    url = LICENSES_URL
    headers = {
        'Authorization': f'Bearer {PERSONAL_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }

    print("Solicitando estado de licencias...")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        active_licenses = data.get('active', 'Desconocido')
        in_use_licenses = data.get('in_use', 'Desconocido')
        return f"Licencias activas: {active_licenses}, Licencias en uso: {in_use_licenses}"
    else:
        return f"Error al obtener el estado de las licencias: {response.status_code}, {response.text}"

# Función para obtener todos los roomIds (espacios donde el bot está presente)
def obtener_room_ids():
    rooms = api.rooms.list()  # Listar los espacios (rooms) a los que el bot tiene acceso
    room_ids = []
    for room in rooms:
        print(f"Nombre del espacio: {room.title}, roomId: {room.id}")  # Imprime el roomId de cada espacio
        room_ids.append(room.id)  # Guarda el roomId en una lista
    return room_ids

# Función para manejar los mensajes del bot
def handle_message(message, room_id):
    print(f"Recibido mensaje: {message.text}")  # Log de depuración
    if message.text:  # Verifica que el mensaje tiene texto
        if 'estado de licencias' in message.text.lower():
            estado_licencias = obtener_estado_licencias()
            response = f"El estado de las licencias es: {estado_licencias}"
        else:
            response = "Lo siento, no entendí tu solicitud. Pregunta por 'estado de licencias'."
        
        # Enviar el mensaje al espacio usando roomId
        print(f"Enviando respuesta: {response}")  # Log de depuración
        api.messages.create(roomId=room_id, text=response)

# Función para escuchar los mensajes del Webex Teams
def listen_for_messages():
    room_ids = obtener_room_ids()  # Obtener todos los roomIds donde el bot está presente
    if not room_ids:
        print("El bot no está en ningún espacio.")
        return
    
    # Seleccionamos el primer roomId (puedes cambiar esta lógica según tus necesidades)
    room_id = room_ids[0]
    
    print(f"Escuchando mensajes en el roomId: {room_id}")  # Log de depuración
    
    # Aquí obtenemos los mensajes del roomId seleccionado
    while True:
        # Obtener los mensajes en tiempo real
        try:
            messages = api.messages.list(roomId=room_id, max=1)  # Obtenemos solo el mensaje más reciente
            if messages:
                for message in messages:
                    handle_message(message, room_id)  # Procesamos los mensajes
        except Exception as e:
            print(f"Error al obtener mensajes: {str(e)}")
        
        time.sleep(5)  # Esperamos 5 segundos antes de hacer una nueva consulta

# Ejecutar la función para escuchar mensajes
if __name__ == '__main__':
    listen_for_messages()



