from flask_socketio import emit
from time import time

def ping_server_socket_cogs():
    # Demande de latence effecuté par le client
    emit('pong', {'timestamp': time()})