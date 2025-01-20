from flask_socketio import emit
from time import time

def heart_beat_cogs(data, database):
    fqdn_data = database.select('''SELECT * from cantina_administration.modules WHERE token = %s''', (data['token']), 1)
    server_time = round(time())
    saved_time = round((data['date']+server_time)/2)

    if fqdn_data[3] == data["fqdn"] and fqdn_data[1] == data["token"]:
        database.exec('''UPDATE cantina_administration.modules SET last_heartbeat = %s, status = 1
                        WHERE token = %s''', (saved_time, data['token']))

        emit('response-heartbeat', {"receive-at": saved_time})
    else:
        emit('error-response', {"message": "token or FQDN invalid"})