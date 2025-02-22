from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length
from functools import wraps
import bcrypt
import os
import socket
from datetime import datetime
import pytz

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/chat_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 3600

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Models
# Table 1: User - Stores user details
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(20), default='offline')
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

# Table 2: Message - Stores message details
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    to_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

    sender = db.relationship('User', foreign_keys=[from_user], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[to_user], backref='received_messages')

# Forms
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Database initialization
with app.app_context():
    db.create_all()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        password = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        if User.query.filter_by(username=username).first():
            form.username.errors.append("Username already exists.")
            return render_template('register.html', form=form)
        
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.checkpw(form.password.data.encode('utf-8'), user.password.encode('utf-8')):
            session.permanent = True
            session['username'] = user.username
            session['user_id'] = user.id
            user.status = 'online'
            user.last_seen = datetime.utcnow()
            db.session.commit()
            socketio.emit('user_status', {'user_id': user.id, 'status': 'online'}, )
            return redirect(url_for('chat_dashboard'))
        form.username.errors.append("Invalid credentials.")
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    user = User.query.get(session['user_id'])
    user.status = 'offline'
    user.last_seen = datetime.utcnow()
    db.session.commit()
    socketio.emit('user_status', {'user_id': user.id, 'status': 'offline'})
    session.clear()
    return redirect(url_for('login'))

@app.route('/chat_dashboard')
@login_required
def chat_dashboard():
    users = User.query.filter(User.id != session['user_id']).all()
    return render_template('chat_dashboard.html', username=session['username'], users=users)

@app.route('/get_messages/<int:receiver_id>')
@login_required
def get_messages(receiver_id):
    sender_id = session['user_id']
    messages = Message.query.filter(
        ((Message.from_user == sender_id) & (Message.to_user == receiver_id)) |
        ((Message.from_user == receiver_id) & (Message.to_user == sender_id))
    ).order_by(Message.timestamp).all()
    
    for msg in messages:
        if msg.to_user == sender_id and not msg.is_read:
            msg.is_read = True
    db.session.commit()

    tz = pytz.timezone('Asia/Kolkata')
    return jsonify([{
        'id': m.id,
        'from_user': m.from_user,
        'to_user': m.to_user,
        'message': m.message,
        'timestamp': m.timestamp.replace(tzinfo=pytz.utc).astimezone(tz).strftime('%Y-%m-%d %H:%M:%S'),
        'is_read': m.is_read
    } for m in messages])

# Socket.IO Events
@socketio.on('connect')
def handle_connect():
    if 'user_id' in session:
        join_room(f"user_{session['user_id']}")
        user = User.query.get(session['user_id'])
        user.status = 'online'
        db.session.commit()
        socketio.emit('user_status', {'user_id': user.id, 'status': 'online'})

@socketio.on('disconnect')
def handle_disconnect():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        user.status = 'offline'
        user.last_seen = datetime.utcnow()
        db.session.commit()
        socketio.emit('user_status', {'user_id': user.id, 'status': 'offline'})
        leave_room(f"user_{session['user_id']}")

@socketio.on('send_message')
def handle_send_message(data):
    sender_id = session['user_id']
    receiver_id = int(data['to_user'])
    message_text = data['message'].strip()
    
    if message_text:
        new_message = Message(from_user=sender_id, to_user=receiver_id, message=message_text)
        db.session.add(new_message)
        db.session.commit()
        
        tz = pytz.timezone('Asia/Kolkata')
        message_data = {
            'msg': message_text,
            'sender_id': sender_id,
            'receiver_id': receiver_id,
            'timestamp': new_message.timestamp.replace(tzinfo=pytz.utc).astimezone(tz).strftime('%Y-%m-%d %H:%M:%S'),
            'is_read': False
        }
        emit('receive_message', message_data, room=f"user_{receiver_id}")
        emit('receive_message', message_data, room=f"user_{sender_id}")

if __name__ == '__main__':
    ip_address = socket.gethostbyname(socket.gethostname())
    print(f"Server running at http://{ip_address}:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)