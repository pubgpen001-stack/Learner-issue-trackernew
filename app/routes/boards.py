from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app.models import (
    create_board, get_board_by_id, get_board_members,
    get_issues_for_board, add_member_to_board, get_user_by_email,
    remove_member_from_board, get_user_by_id, delete_board
)
from app.utils.decorators import board_member_required

boards_bp = Blueprint('boards', __name__)

# Decorator to restrict routes to lecturers only
def lecturer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'lecturer':
            flash('Only lecturers can access this page.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@boards_bp.route('/create-board', methods=['GET', 'POST'])
@login_required
@lecturer_required
def create_board_route():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        course_code = request.form.get('course_code', '').strip()
        description = request.form.get('description', '').strip()

        if not name or not course_code:
            flash('Board name and course code are required.', 'danger')
            return redirect(url_for('boards.create_board'))

        board_id = create_board(name, course_code, description, current_user.id)
        flash('Board created successfully.', 'success')
        return redirect(url_for('boards.view_board', board_id=board_id))

    return render_template('create_board.html')

@boards_bp.route('/board/<int:board_id>')
@login_required
@board_member_required
def view_board(board_id):
    board = get_board_by_id(board_id)
    if not board:
        flash('Board not found.', 'danger')
        return redirect(url_for('main.dashboard'))

    members = get_board_members(board_id)
    issues = get_issues_for_board(board_id)

    return render_template('board.html', board=board, members=members, issues=issues)

@boards_bp.route('/board/<int:board_id>/invite', methods=['POST'])
@login_required
@lecturer_required
def invite_member(board_id):
    board = get_board_by_id(board_id)
    if not board:
        flash('Board not found.', 'danger')
        return redirect(url_for('main.dashboard'))

    if board['created_by'] != current_user.id:
        flash('You can only invite members to your own boards.', 'danger')
        return redirect(url_for('boards.view_board', board_id=board_id))

    email = request.form.get('email', '').strip().lower()
    role_on_board = request.form.get('role_on_board', '')

    if not email or role_on_board not in ('student', 'tutor'):
        flash('Please provide a valid email and role.', 'danger')
        return redirect(url_for('boards.view_board', board_id=board_id))

    user = get_user_by_email(email)
    if not user:
        flash('No user found with that email.', 'danger')
        return redirect(url_for('boards.view_board', board_id=board_id))

    if user.id == current_user.id:
        flash('You cannot invite yourself.', 'danger')
        return redirect(url_for('boards.view_board', board_id=board_id))

    if user.role == 'student' and role_on_board == 'tutor':
        flash('A registered student cannot be invited as a tutor.', 'danger')
        return redirect(url_for('boards.view_board', board_id=board_id))

    add_member_to_board(board_id, user.id, role_on_board)
    flash(f'{user.username} has been added to the board.', 'success')
    return redirect(url_for('boards.view_board', board_id=board_id))

@boards_bp.route('/board/<int:board_id>/remove/<int:user_id>', methods=['POST'])
@login_required
@lecturer_required
def remove_member(board_id, user_id):
    board = get_board_by_id(board_id)
    if not board:
        flash('Board not found.', 'danger')
        return redirect(url_for('main.dashboard'))

    if board['created_by'] != current_user.id:
        flash('You can only remove members from your own boards.', 'danger')
        return redirect(url_for('boards.view_board', board_id=board_id))

    user = get_user_by_id(user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('boards.view_board', board_id=board_id))
    
    if user.id == current_user.id:
        flash('You cannot remove yourself from the board.', 'danger')
        return redirect(url_for('boards.view_board', board_id=board_id))

    remove_member_from_board(board_id, user_id)
    flash(f'{user.username} has been removed from the board.', 'danger')
    return redirect(url_for('boards.view_board', board_id=board_id))

@boards_bp.route('/board/<int:board_id>/delete', methods=['POST'])
@login_required
@lecturer_required
def delete_board_route(board_id):
    board = get_board_by_id(board_id)
    if not board:
        flash('Board not found.', 'danger')
        return redirect(url_for('main.dashboard'))

    if board['created_by'] != current_user.id:
        flash('Only the creator of the board can delete it.', 'danger')
        return redirect(url_for('main.dashboard'))

    delete_board(board_id)
    flash(f"Board '{board['name']}' has been permanently deleted.", 'success')
    return redirect(url_for('main.dashboard'))