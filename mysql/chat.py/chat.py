# from flask import Blueprint, render_template, session, redirect, url_for, g
# from flask_socketio import emit, join_room
# from app import socketio, db
# import mysql.connector

# # Define User and Message Models
# class User():
#     def __init__(self, id, username, password):
#         self.id = id
#         self.username = username
#         self.password = password

#     def __repr__(self):
#         return f'<User {self.username}>'

# class Message():
#     def __init__(self, id, from_user, to_user, content):
#         self.id = id
#         self.from_user = from_user
#         self.to_user = to_user
#         self.content = content

#     def __repr__(self):
#         return f'<Message from {self.from_user} to {self.to_user}>'

# # Create a Blueprint for chat functionality
# chat_bp = Blueprint('chat', __name__)

# @chat_bp.route('/chat')
# def chat():
#     # Ensure the user is logged in
#     if 'user_id' not in session:
#         return redirect(url_for('login'))

#     # Fetch all users except the logged-in user to display in the user list
#     current_user_id = session['user_id']
#     users = fetch_users(current_user_id)

#     return render_template('chat_dashboard.html', users=users)

# @socketio.on('join')
# def handle_join(data):
#     # Join a room for private messaging
#     join_room(data['room'])

# @socketio.on('send_message')
# def handle_send_message(data):
#     # Retrieve sender ID from session
#     from_user_id = session.get('user_id')

#     # Create a new message object and store it in the database
#     to_user_id = data['to_user']
#     content = data['message']
    
#     insert_message(from_user_id, to_user_id, content)

#     # Emit the message to both sender and recipient's rooms
#     emit('receive_message', {
#         'msg': content,
#         'from_user': from_user_id,
#         'to_user': to_user_id
#     }, room=data['room'])

# # Helper function to fetch users from the database
# def fetch_users(current_user_id):
#     try:
#         db_connection = mysql.connector.connect(
#             host="localhost",
#             user="root",
#             password="",
#             database="chat_app"
#         )
#         cursor = db_connection.cursor()
#         cursor.execute("SELECT id, username, password FROM user WHERE id != %s", (current_user_id,))
#         users = []
#         for (id, username, password) in cursor:
#             user = User(id=id, username=username, password=password)
#             users.append(user)
#     except mysql.connector.Error as err:
#         print(f"Error: {err}")
#         users = []
#     finally:
#         if db_connection:
#             cursor.close()
#             db_connection.close()
#     return users

# # Helper function to insert a message into the database
# def insert_message(from_user_id, to_user_id, content):
#     try:
#         db_connection = mysql.connector.connect(
#             host="localhost",
#             user="root",
#             password="",
#             database="chat_app"
#         )
#         cursor = db_connection.cursor()
#         cursor.execute(
#             "INSERT INTO message (from_user, to_user, content) VALUES (%s, %s, %s)",
#             (from_user_id, to_user_id, content)
#         )
#         db_connection.commit()
#     except mysql.connector.Error as err:
#         print(f"Error: {err}")
#     finally:
#         if db_connection:
#             cursor.close()
#             db_connection.close()
