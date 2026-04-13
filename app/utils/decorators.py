from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user
from app.models import get_board_by_id, is_issue_member, get_board_members

def is_board_member(board_id, user_id):
    board = get_board_by_id(board_id)
    if not board:
        return False
    if board['created_by'] == user_id:
        return True
    
    members = get_board_members(board_id)
    return any(member['id'] == user_id for member in members)

def board_member_required(f):
    @wraps(f)
    def decorated_function(board_id, *args, **kwargs):
        if not is_board_member(board_id, current_user.id):
            flash('Access denied. You are not a member of this board.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(board_id, *args, **kwargs)
    return decorated_function
