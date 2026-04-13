import sqlite3
import os

DATABASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'tracker.db')

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    with open('schema.sql', 'r') as f:
        cursor.executescript(f.read())

    print("Tables created successfully.")

    # Seed test data
    from werkzeug.security import generate_password_hash

    cursor.execute(
        "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
        ('Dr Smith', 'lecturer@test.com', generate_password_hash('password123'), 'lecturer')
    )
    cursor.execute(
        "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
        ('John Student', 'student@test.com', generate_password_hash('password123'), 'student')
    )
    cursor.execute(
        "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
        ('Jane Tutor', 'tutor@test.com', generate_password_hash('password123'), 'tutor')
    )

    print("Test users created:")
    print("  Lecturer: lecturer@test.com / password123")
    print("  Student:  student@test.com / password123")
    print("  Tutor:    tutor@test.com / password123")

    conn.commit()
    conn.close()
    print("Database initialised successfully.")

if __name__ == '__main__':
    init_db()