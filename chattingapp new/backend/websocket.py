from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

@socketio.on('message')
def handle_message(data):
    """Handle incoming messages and broadcast them to users."""
    socketio.send(data)  # Broadcast received message to all clients.

if __name__ == '__main__':
    socketio.run(app)
