from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import get_boards_for_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('home.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    boards = get_boards_for_user(current_user.id, current_user.role)
    return render_template('dashboard.html', boards=boards)