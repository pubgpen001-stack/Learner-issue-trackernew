from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from app.models import (
    get_board_by_id, create_issue, get_issue_by_id,
    join_issue, is_issue_member, get_issue_members,
    get_messages_for_issue, delete_issue, delete_message, get_message_by_id
)
from app.utils import find_similar_issues
from app.utils.moderation import check_content
from app.utils.decorators import board_member_required, is_board_member

issues_bp = Blueprint('issues', __name__)

@issues_bp.route('/board/<int:board_id>/create-issue', methods=['GET', 'POST'])
@login_required
@board_member_required
def create_issue_route(board_id):
    board = get_board_by_id(board_id)
    if not board:
        flash('Board not found.', 'danger')
        return redirect(url_for('main.dashboard'))

    similar_issues = []

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        confirmed = request.form.get('confirmed', '')

        if not title:
            flash('Issue title is required.', 'danger')
            return redirect(url_for('issues.create_issue_route', board_id=board_id))

        # If user hasn't confirmed yet, check for similar issues
        if confirmed != 'yes':
            similar_issues = find_similar_issues(title, description, board_id)
            if similar_issues:
                return render_template('create_issue.html', board=board,
                                       similar_issues=similar_issues,
                                       title=title, description=description)

        # No similar issues found, or user confirmed they want to create anyway
        is_flagged = check_content(title + " " + description)
        issue_id = create_issue(board_id, title, description, current_user.id, is_flagged)
        flash('Issue created successfully.', 'success')
        return redirect(url_for('issues.view_issue', issue_id=issue_id))

    return render_template('create_issue.html', board=board, similar_issues=[],
                           title='', description='')

@issues_bp.route('/issue/<int:issue_id>')
@login_required
def view_issue(issue_id):
    issue = get_issue_by_id(issue_id)
    if not issue:
        flash('Issue not found.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    if not is_board_member(issue['board_id'], current_user.id):
        flash('Access denied. You are not a member of this board.', 'danger')
        return redirect(url_for('main.dashboard'))

    members = get_issue_members(issue_id)
    messages = get_messages_for_issue(issue_id)
    is_member = is_issue_member(issue_id, current_user.id)

    return render_template('issue.html', issue=issue, members=members, messages=messages, is_member=is_member)

@issues_bp.route('/issue/<int:issue_id>/join', methods=['POST'])
@login_required
def join_issue_route(issue_id):
    issue = get_issue_by_id(issue_id)
    if not issue:
        flash('Issue not found.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    if not is_board_member(issue['board_id'], current_user.id):
        flash('Access denied. You are not a member of this board.', 'danger')
        return redirect(url_for('main.dashboard'))

    if is_issue_member(issue_id, current_user.id):
        flash('You are already a member of this issue.', 'info')
    else:
        join_issue(issue_id, current_user.id)
        flash('You have joined this issue.', 'success')

    return redirect(url_for('issues.view_issue', issue_id=issue_id))

@issues_bp.route('/issue/<int:issue_id>/delete', methods=['POST'])
@login_required
def delete_issue_route(issue_id):
    issue = get_issue_by_id(issue_id)
    if not issue:
        flash('Issue not found.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    if not is_board_member(issue['board_id'], current_user.id):
        flash('Access denied. You are not a member of this board.', 'danger')
        return redirect(url_for('main.dashboard'))

    board = get_board_by_id(issue['board_id'])
    # Only board creator or issue creator (if they are still a valid member/staff, but issue creator implies they have rights over their issue) or a lecturer/tutor on the board can delete.
    # To keep it simple and robust per instructions:
    # "For deletion, verify the user is the board creator OR has a legitimate lecturer/tutor role"
    from app.models import get_board_members
    is_staff = False
    if board['created_by'] == current_user.id:
        is_staff = True
    else:
        for member in get_board_members(issue['board_id']):
            if member['id'] == current_user.id and member['role_on_board'] in ('tutor',):
                is_staff = True
                break

    if not is_staff and issue['created_by'] != current_user.id:
        flash('You do not have permission to delete this issue.', 'danger')
        return redirect(url_for('boards.view_board', board_id=issue['board_id']))

    board_id = issue['board_id']
    delete_issue(issue_id)
    flash('Issue has been successfully deleted.', 'success')
    return redirect(url_for('boards.view_board', board_id=board_id))

@issues_bp.route('/message/<int:message_id>/delete', methods=['POST'])
@login_required
def delete_message_route(message_id):
    msg = get_message_by_id(message_id)
    if not msg:
        flash('Message not found.', 'danger')
        return redirect(request.referrer or url_for('main.dashboard'))

    issue_id = msg['issue_id']
    from app.models import get_issue_by_id, get_board_by_id, get_board_members
    issue = get_issue_by_id(issue_id)
    
    if not issue or not is_board_member(issue['board_id'], current_user.id):
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    board = get_board_by_id(issue['board_id'])
    is_staff = False
    if board['created_by'] == current_user.id:
        is_staff = True
    else:
        for member in get_board_members(issue['board_id']):
            if member['id'] == current_user.id and member['role_on_board'] in ('tutor',):
                is_staff = True
                break

    if not is_staff and msg['user_id'] != current_user.id:
        flash('You do not have permission to delete this message.', 'danger')
        return redirect(url_for('issues.view_issue', issue_id=issue_id))

    delete_message(message_id)
    # Usually we flash, but for quick message deletes we might just reload the page and let the UI speak for itself or flash a clean toast.
    flash('Message has been removed.', 'success')
    return redirect(url_for('issues.view_issue', issue_id=issue_id))