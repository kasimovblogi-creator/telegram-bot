import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    referrer_id INTEGER,
    points INTEGER DEFAULT 0,
    referrals INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    last_bonus TEXT
)
""")

conn.commit()
conn.close()

print("DB tayyor")