from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())

    sender = db.relationship('User', foreign_keys=[from_user], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[to_user], backref='received_messages')

    def __repr__(self):
        return f'<Message from {self.sender.username} to {self.receiver.username}: {self.message}>'
