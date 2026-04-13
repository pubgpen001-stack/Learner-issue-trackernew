import sqlite3
from flask import g, current_app
from flask_login import UserMixin

# ── Database connection ──

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# ── User model for Flask-Login ──

class User(UserMixin):
    def __init__(self, id, username, email, password_hash, role):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role

# ── User functions ──

def get_user_by_id(user_id):
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if row:
        return User(row['id'], row['username'], row['email'], row['password_hash'], row['role'])
    return None

def get_user_by_email(email):
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if row:
        return User(row['id'], row['username'], row['email'], row['password_hash'], row['role'])
    return None

def create_user(username, email, password_hash, role):
    db = get_db()
    db.execute(
        "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
        (username, email, password_hash, role)
    )
    db.commit()

# ── Board functions ──

def create_board(name, course_code, description, created_by):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO boards (name, course_code, description, created_by) VALUES (?, ?, ?, ?)",
        (name, course_code, description, created_by)
    )
    db.commit()
    return cursor.lastrowid

def get_boards_for_user(user_id, role):
    db = get_db()
    if role == 'lecturer':
        return db.execute(
            "SELECT * FROM boards WHERE created_by = ? ORDER BY created_at DESC", (user_id,)
        ).fetchall()
    else:
        return db.execute(
            """SELECT b.* FROM boards b
               JOIN board_members bm ON b.id = bm.board_id
               WHERE bm.user_id = ?
               ORDER BY b.created_at DESC""", (user_id,)
        ).fetchall()

def get_board_by_id(board_id):
    db = get_db()
    return db.execute("SELECT * FROM boards WHERE id = ?", (board_id,)).fetchone()

def add_member_to_board(board_id, user_id, role_on_board):
    db = get_db()
    db.execute(
        "INSERT OR IGNORE INTO board_members (board_id, user_id, role_on_board) VALUES (?, ?, ?)",
        (board_id, user_id, role_on_board)
    )
    db.commit()

def get_board_members(board_id):
    db = get_db()
    return db.execute(
        """SELECT u.id, u.username, u.email, bm.role_on_board
           FROM users u JOIN board_members bm ON u.id = bm.user_id
           WHERE bm.board_id = ?""", (board_id,)
    ).fetchall()

def remove_member_from_board(board_id, user_id):
    db = get_db()
    db.execute(
        "DELETE FROM board_members WHERE board_id = ? AND user_id = ?",
        (board_id, user_id)
    )
    db.commit()

def delete_board(board_id):
    db = get_db()
    db.execute("DELETE FROM boards WHERE id = ?", (board_id,))
    db.commit()

# ── Issue functions ──

def create_issue(board_id, title, description, created_by, is_flagged=False):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO issues (board_id, title, description, created_by, is_flagged) VALUES (?, ?, ?, ?, ?)",
        (board_id, title, description, created_by, is_flagged)
    )
    issue_id = cursor.lastrowid

    # Add creator as issue member
    db.execute(
        "INSERT INTO issue_members (issue_id, user_id) VALUES (?, ?)",
        (issue_id, created_by)
    )

    # Add all tutors on the board as issue members
    tutors = db.execute(
        "SELECT user_id FROM board_members WHERE board_id = ? AND role_on_board = 'tutor'",
        (board_id,)
    ).fetchall()
    for tutor in tutors:
        db.execute(
            "INSERT OR IGNORE INTO issue_members (issue_id, user_id) VALUES (?, ?)",
            (issue_id, tutor['user_id'])
        )

    db.commit()
    return issue_id

def get_issues_for_board(board_id):
    db = get_db()
    return db.execute(
        """SELECT i.*, u.username as creator_name,
           (SELECT COUNT(*) FROM issue_members WHERE issue_id = i.id) as member_count
           FROM issues i JOIN users u ON i.created_by = u.id
           WHERE i.board_id = ?
           ORDER BY i.created_at DESC""", (board_id,)
    ).fetchall()

def get_issue_by_id(issue_id):
    db = get_db()
    return db.execute(
        """SELECT i.*, u.username as creator_name, b.name as board_name, b.id as board_id
           FROM issues i
           JOIN users u ON i.created_by = u.id
           JOIN boards b ON i.board_id = b.id
           WHERE i.id = ?""", (issue_id,)
    ).fetchone()

def join_issue(issue_id, user_id):
    db = get_db()
    db.execute(
        "INSERT OR IGNORE INTO issue_members (issue_id, user_id) VALUES (?, ?)",
        (issue_id, user_id)
    )
    db.commit()

def is_issue_member(issue_id, user_id):
    db = get_db()
    row = db.execute(
        "SELECT * FROM issue_members WHERE issue_id = ? AND user_id = ?",
        (issue_id, user_id)
    ).fetchone()
    return row is not None

def get_issue_members(issue_id):
    db = get_db()
    return db.execute(
        """SELECT u.id, u.username, u.role
           FROM users u JOIN issue_members im ON u.id = im.user_id
           WHERE im.issue_id = ?""", (issue_id,)
    ).fetchall()

def delete_issue(issue_id):
    db = get_db()
    db.execute("DELETE FROM issues WHERE id = ?", (issue_id,))
    db.commit()

# ── Message functions ──

def create_message(issue_id, user_id, content, is_flagged=False):
    db = get_db()
    db.execute(
        "INSERT INTO messages (issue_id, user_id, content, is_flagged) VALUES (?, ?, ?, ?)",
        (issue_id, user_id, content, is_flagged)
    )
    db.commit()

def get_messages_for_issue(issue_id):
    db = get_db()
    return db.execute(
        """SELECT m.*, u.username
           FROM messages m JOIN users u ON m.user_id = u.id
           WHERE m.issue_id = ?
           ORDER BY m.sent_at ASC""", (issue_id,)
    ).fetchall()

def get_message_by_id(message_id):
    db = get_db()
    return db.execute("SELECT * FROM messages WHERE id = ?", (message_id,)).fetchone()

def delete_message(message_id):
    db = get_db()
    db.execute("DELETE FROM messages WHERE id = ?", (message_id,))
    db.commit()