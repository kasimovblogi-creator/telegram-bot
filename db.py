import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")


def get_conn():
    return psycopg2.connect(DATABASE_URL, sslmode="require")


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS saudiasaribot (
        user_id BIGINT PRIMARY KEY
    )
    """)

    conn.commit()
    conn.close()


def add_user(user_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO saudiasaribot (user_id)
    VALUES (%s)
    ON CONFLICT (user_id) DO NOTHING
    """, (user_id,))

    conn.commit()
    conn.close()


def get_user_count():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM saudiasaribot")
    count = cur.fetchone()[0]

    conn.close()
    return count