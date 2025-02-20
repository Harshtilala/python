from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from forms import RegistrationForm, LoginForm
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import os
from flask_socketio import SocketIO, emit, join_room, leave_room
import socket
from datetime import datetime
import pytz

# Initialize Flask app
app = Flask(__name__)

# Database Configuration
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/chat_App'  # Replace with your actual database URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy and SocketIO
db = SQLAlchemy(app)
socketio = SocketIO(app)

# User Model
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

# Message Model
class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    from_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    to_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())  # Ensure this column exists

    sender = db.relationship('User', foreign_keys=[from_user], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[to_user], backref='received_messages')

    def __repr__(self):
        return f'<Message from {self.sender.username} to {self.receiver.username}: {self.message}>'

# Create the database tables (run this ONCE)
with app.app_context():
    db.create_all()

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            form.username.errors.append("Username already exists.")
            return render_template('register.html', form=form)

        new_user = User(username=username, password=hashed_password.decode('utf-8'))
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            session['username'] = username
            session['user_id'] = user.id  # Store user ID in session
            return redirect(url_for('chat_dashboard'))
        else:
            form.username.errors.append("Invalid username or password.")
            return render_template('login.html', form=form)

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/chat_dashboard')
@login_required
def chat_dashboard():
    username = session['username']
    user_id = session['user_id']
    users = User.query.filter(User.id != user_id).all()
    return render_template('chat_dashboard.html', username=username, users=users)

@app.route('/get_messages/<int:receiver_id>')
@login_required
def get_messages(receiver_id):
    sender_id = session['user_id']
    
    # Fetch messages between the sender and receiver sorted by timestamp.
    messages = Message.query.filter(
        ((Message.from_user == sender_id) & (Message.to_user == receiver_id)) |
        ((Message.from_user == receiver_id) & (Message.to_user == sender_id))
    ).order_by(Message.timestamp).all()

    messages_list = []
    
    for message in messages:
        timestamp_str = message.timestamp.strftime('%Y-%m-%d %H:%M:%S')  # Format timestamp as string.
        
        messages_list.append({
            'id': message.id,
            'from_user': message.from_user,
            'to_user': message.to_user,
            'message': message.message,
            'timestamp': timestamp_str,
        })
    
    return jsonify(messages_list)

# Socket.IO event for sending messages
@socketio.on('send_message')
def handle_send_message(data):
    sender_id = session['user_id']
    receiver_id = data['to_user']
    message_text = data['message']

    try:
        new_message = Message(from_user=sender_id, to_user=receiver_id, message=message_text)
        
        # Add the new message to the database.
        db.session.add(new_message)
        db.session.commit()

        # Format timestamp as string for display.
        timestamp_str = new_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')

        # Emit the message to both the sender's and receiver's rooms.
        emit(
            'receive_message',
            {'msg': message_text, 'sender_id': sender_id, 'timestamp': timestamp_str},
            room=f'user_{receiver_id}'
        )
        
        emit(
            'receive_message',
            {'msg': message_text, 'sender_id': sender_id, 'timestamp': timestamp_str},
            room=f'user_{sender_id}'
        )

    except Exception as e:
        print(f"Error saving message: {e}")
        db.session.rollback()  # Rollback in case of error.

# Socket.IO event for connecting a user
@socketio.on('connect')
def handle_connect():
    user_id = session.get('user_id')
    
    if user_id:
        print(f"User {user_id} connected")
        
        # Join a room named after the user's ID.
        join_room(f'user_{user_id}')

@socketio.on('disconnect')
def handle_disconnect():
    user_id = session.get('user_id')
    
    if user_id:
        print(f"User {user_id} disconnected")
        
        # Leave the room named after the user's ID.
        leave_room(f'user_{user_id}')

if __name__ == '__main__':
    print("Server running at http://127.0.0.1:5000")
    
    socketio.run(app, host='0.0.0.0', debug=True)  # Change host as needed for your setup.
