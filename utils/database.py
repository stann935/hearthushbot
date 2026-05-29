import sqlite3
import os
from datetime import date
from config import DB_PATH

def get_connection():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id     INTEGER PRIMARY KEY,
            username    TEXT,
            first_name  TEXT,
            is_premium  INTEGER DEFAULT 0,
            joined_at   TEXT DEFAULT (datetime('now')),
            total_msgs  INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS messages (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER,
            role       TEXT,
            content    TEXT,
            category   TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS usage (
            user_id INTEGER,
            date    TEXT,
            count   INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, date)
        );

        CREATE TABLE IF NOT EXISTS leads (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER,
            problem_type TEXT,
            summary      TEXT,
            created_at   TEXT DEFAULT (datetime('now'))
        );
    """)
    conn.commit()
    conn.close()

def upsert_user(user_id, username, first_name):
    conn = get_connection()
    conn.execute("""
        INSERT INTO users (user_id, username, first_name)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username,
            first_name = excluded.first_name,
            total_msgs = total_msgs + 1
    """, (user_id, username, first_name))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE user_id = ?", (user_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None

def is_premium(user_id):
    user = get_user(user_id)
    return bool(user and user["is_premium"])

def get_daily_usage(user_id):
    today = str(date.today())
    conn = get_connection()
    row = conn.execute(
        "SELECT count FROM usage WHERE user_id = ? AND date = ?",
        (user_id, today)
    ).fetchone()
    conn.close()
    return row["count"] if row else 0

def increment_usage(user_id):
    today = str(date.today())
    conn = get_connection()
    conn.execute("""
        INSERT INTO usage (user_id, date, count) VALUES (?, ?, 1)
        ON CONFLICT(user_id, date) DO UPDATE SET count = count + 1
    """, (user_id, today))
    conn.commit()
    conn.close()

def is_within_limit(user_id):
    from config import FREE_DAILY_LIMIT
    if is_premium(user_id):
        return True
    return get_daily_usage(user_id) < FREE_DAILY_LIMIT

def save_message(user_id, role, content, category=""):
    conn = get_connection()
    conn.execute("""
        INSERT INTO messages (user_id, role, content, category)
        VALUES (?, ?, ?, ?)
    """, (user_id, role, content, category))
    conn.commit()
    conn.close()

def get_history(user_id, limit=16):
    conn = get_connection()
    rows = conn.execute("""
        SELECT role, content FROM messages
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (user_id, limit)).fetchall()
    conn.close()
    return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]

def clear_history(user_id):
    conn = get_connection()
    conn.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def save_lead(user_id, problem_type, summary):
    conn = get_connection()
    conn.execute("""
        INSERT INTO leads (user_id, problem_type, summary)
        VALUES (?, ?, ?)
    """, (user_id, problem_type, summary))
    conn.commit()
    conn.close()

def get_stats():
    conn = get_connection()
    total_users = conn.execute(
        "SELECT COUNT(*) as n FROM users"
    ).fetchone()["n"]
    premium_users = conn.execute(
        "SELECT COUNT(*) as n FROM users WHERE is_premium = 1"
    ).fetchone()["n"]
    total_messages = conn.execute(
        "SELECT COUNT(*) as n FROM messages"
    ).fetchone()["n"]
    active_today = conn.execute(
        "SELECT COUNT(DISTINCT user_id) as n FROM usage WHERE date = ?",
        (str(date.today()),)
    ).fetchone()["n"]
    conn.close()
    return {
        "total_users": total_users,
        "premium_users": premium_users,
        "total_messages": total_messages,
        "active_today": active_today
    }
