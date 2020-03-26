from dotenv import load_dotenv
load_dotenv()
from os import getenv
from engineio.payload import Payload
Payload.max_decode_packets = 500
from flask_socketio import SocketIO, join_room, leave_room, send, emit, close_room
import datetime
from flask import Flask, stream_with_context, Response, request, render_template, send_from_directory, abort, jsonify

app = Flask(__name__)
sio = SocketIO(app)

# @todo oauth authentication
# from db import connect, migrate, connection, insert_key, get_key, delete_key

# if connect() is False:
#     print('Database failed to connect')
# else:
#     migrate()

def write_log(s):
    with open('logfile.out', 'a+') as f:
        f.write('time: %s Action: %s \n' % (str(datetime.datetime.now()), s))

@app.route('/', methods=['GET'])
def home():
    return render_template("stream.html")

@app.route('/live/<room>')
def show_client(room):
    return render_template('remote.html', room=room)

rooms = {}

@app.route('/rooms/<room>')
def get_room(room):
    try:
        return jsonify(rooms[room])
    except KeyError:
        abort(404)

@app.route('/stream/<path:path>', methods=['GET'])
def stream(path):
    return send_from_directory('out', path)

@sio.on('data', namespace='/')
def data(inbound):
    print('data', inbound['room'], request.sid)
    emit('data', inbound['data'], room=inbound['room'], include_self=False)

@sio.on('connect', namespace='/')
def connect():
    print('connect', request.sid)

@sio.on('disconnect', namespace='/')
def disconnect():
    print('disconnect', request.sid)

@sio.on('leave', namespace='/')
def leave(room):
    print('leave', room, request.sid)
    leave_room(room)
    try:
        try:
            rooms[room].remove(request.sid)
            emit('left', request.sid, room=room, include_self=False)
        except ValueError:
            print(request.sid, 'doesnt exist in room', room)
        if (len(rooms[room]) == 0):
            close_room(room)
            del rooms[room]
            print('closed', room)
            emit('closed', room)
    except KeyError:
        print('room', room, 'doesnt exist')

@sio.on('join', namespace='/')
def join(room):
    print('join', room, request.sid)
    join_room(room)
    try:
        rooms[room].append(request.sid)
    except KeyError:
        print('created room', room)
        rooms[room] = [request.sid]
        emit('opened', room)
    
    print('joined room', room, request.sid)
    emit('ready', room=room, include_self=False)

if __name__ == "__main__":
    port = getenv('PORT')
    sio.run(app, port=port, debug=True)