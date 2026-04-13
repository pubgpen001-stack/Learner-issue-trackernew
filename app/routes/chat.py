from flask_socketio import emit, join_room, leave_room, disconnect
from flask_login import current_user
from app import socketio
from app.models import create_message, get_issue_by_id
from app.utils.moderation import check_content
from app.utils.decorators import is_board_member

@socketio.on('join_room')
def handle_join(data):
    if not current_user.is_authenticated:
        disconnect()
        return

    issue_id = data.get('issue_id')
    if not issue_id:
        return
        
    issue = get_issue_by_id(issue_id)
    if not issue or not is_board_member(issue['board_id'], current_user.id):
        return

    room = f"issue_{issue_id}"
    join_room(room)

@socketio.on('leave_room')
def handle_leave(data):
    if not current_user.is_authenticated:
        return
        
    issue_id = data.get('issue_id')
    if not issue_id:
        return
        
    room = f"issue_{issue_id}"
    leave_room(room)

@socketio.on('send_message')
def handle_message(data):
    if not current_user.is_authenticated:
        disconnect()
        return

    issue_id = data.get('issue_id')
    content = data.get('content', '').strip()

    if not issue_id or not content:
        return

    issue = get_issue_by_id(issue_id)
    if not issue or not is_board_member(issue['board_id'], current_user.id):
        return

    is_flagged = check_content(content)
    create_message(issue_id, current_user.id, content, is_flagged)

    room = f"issue_{issue_id}"
    emit('new_message', {
        'username': current_user.username,
        'content': content,
        'sent_at': 'Just now',
        'is_flagged': is_flagged
    }, room=room)