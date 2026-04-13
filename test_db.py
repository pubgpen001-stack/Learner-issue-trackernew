import sqlite3
conn = sqlite3.connect('app.db')
c = conn.cursor()
c.execute("SELECT id, name, created_by FROM boards WHERE id=1")
print("Board 1:", c.fetchone())
c.execute("SELECT id, email, role FROM users WHERE email='lecturer@test.com'")
print("Lecturer:", c.fetchone())
