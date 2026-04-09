from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey123'
socketio = SocketIO(app, cors_allowed_origins="*")

users = {}
messages = []

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def on_connect():
    print(f"Connected: {request.sid}")

@socketio.on('set_username')
def set_username(data):
    username = data['username']
    avatar = data.get('avatar', '😊')
    users[request.sid] = {'name': username, 'avatar': avatar}
    emit('username_set', {'username': username, 'avatar': avatar})
    emit('user_joined', {
        'username': username,
        'avatar': avatar,
        'online_users': list(users.values()),
        'time': datetime.now().strftime("%H:%M")
    }, broadcast=True)
    emit('chat_history', {'messages': messages})

@socketio.on('send_message')
def send_message(data):
    user = users.get(request.sid, {'name': 'Unknown', 'avatar': '😊'})
    msg = {
        'username': user['name'],
        'avatar': user['avatar'],
        'message': data['message'],
        'time': datetime.now().strftime("%H:%M")
    }
    messages.append(msg)
    emit('receive_message', msg, broadcast=True)

@socketio.on('typing')
def typing(data):
    user = users.get(request.sid, {'name': '', 'avatar': ''})
    emit('user_typing', {'username': user['name']}, broadcast=True, include_self=False)

@socketio.on('stop_typing')
def stop_typing():
    emit('user_stop_typing', {}, broadcast=True, include_self=False)

@socketio.on('disconnect')
def on_disconnect():
    user = users.pop(request.sid, {'name': 'Someone', 'avatar': ''})
    emit('user_left', {
        'username': user['name'],
        'online_users': list(users.values()),
        'time': datetime.now().strftime("%H:%M")
    }, broadcast=True)
    print(f"Disconnected: {user['name']}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)