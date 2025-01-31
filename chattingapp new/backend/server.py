from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from backend.database import Database

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

db = Database()

@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    email = request.json.get('email')
    mobile_number = request.json.get('mobile_number')
    password = request.json.get('password')
    
    # Hash password here (use bcrypt or similar)
    
    query = "INSERT INTO users (username, email, mobile_number, password) VALUES (%s, %s, %s, %s)"
    db.execute_query(query, (username, email, mobile_number, password))
    
    return jsonify({"message": "User registered successfully!"})

@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')
    
    # Verify password here
    
    return jsonify({"message": "Login successful!"})

@socketio.on('send_message')
def handle_send_message(data):
    from_user = data['from_user']
    to_user = data['to_user']
    message = data['message']
    
    query = "INSERT INTO messages (from_user, to_user, message) VALUES (%s, %s, %s)"
    db.execute_query(query, (from_user, to_user, message))
    
    socketio.emit('receive_message', data)

if __name__ == '__main__':
    socketio.run(app)
