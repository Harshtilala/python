from flask import Blueprint, render_template, session
from app import login_required, User

chat_dashboard_bp = Blueprint('chat_dashboard', __name__)

@chat_dashboard_bp.route('/chat_dashboard')
@login_required
def chat_dashboard():
    username = session['username']
    user = User.query.filter_by(username=username).first()
    return render_template('chat_dashboard.html', username=username, user=user)
