from flask import Flask, render_template, request, redirect, url_for, session
from forms import RegistrationForm, LoginForm  # Ensure you have these forms defined in a separate file
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import os
from flask_socketio import SocketIO, emit

app = Flask(__name__)

# Database Configuration
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/chat_app'  # Replace with your actual database URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
socketio = SocketIO(app)  # Socket.IO object

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

# Message Model
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')

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

@app.route('/users')
@login_required
def user_list():
    users = User.query.all()
    return render_template('user_list.html', users=users)

@app.route('/profile')
@login_required
def profile():
    username = session.get('username')
    user = User.query.filter_by(username=username).first()

    if user:
        return render_template('profile.html', user=user)

    return "User not found", 404

@app.route('/success')
def success():
    return "Registration successful!"

# Socket.IO event for sending messages
@socketio.on('send_message')
def handle_send_message(data):
    sender_id = session['user_id']
    receiver_id = data['to_user']
    message_text = data['message']

    try:
        new_message = Message(sender_id=sender_id, receiver_id=receiver_id, message=message_text)
        db.session.add(new_message)
        db.session.commit()

        # Emit the message to the receiver
        emit('receive_message', {'msg': message_text, 'sender_id': sender_id}, room=receiver_id)

        # Emit the message back to the sender for immediate display
        emit('receive_message', {'msg': message_text, 'sender_id': sender_id}, room=sender_id)

    except Exception as e:
        print(f"Error saving message: {e}")
        db.session.rollback()  # Rollback in case of error

# Socket.IO event for connecting a user
@socketio.on('connect')
def handle_connect():
    user_id = session.get('user_id')
    if user_id:
        print(f"User {user_id} connected")
        # Join a room named after the user's ID (optional for further functionality)
        
    else:
        print("User connected without a user_id in session")

if __name__ == '__main__':
     socketio.run(app, host='0.0.0.0', debug=True)  # Change host as needed for your setup
