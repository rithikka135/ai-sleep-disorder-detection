"""
Database module - SQLite with users and sleep_data tables
"""
import sqlite3, hashlib, os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "sleep_app.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email    TEXT,
            created  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS sleep_data (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            username          TEXT NOT NULL,
            movement          REAL NOT NULL,
            noise             REAL NOT NULL,
            screen            INTEGER NOT NULL,
            predicted_disorder TEXT NOT NULL,
            sleep_score       INTEGER NOT NULL,
            confidence        REAL DEFAULT 0,
            notes             TEXT,
            recorded_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    # Seed demo user
    pw_hash = hashlib.sha256("demo123".encode()).hexdigest()
    cur.execute("INSERT OR IGNORE INTO users (username, password, email) VALUES (?, ?, ?)",
                ("demo", pw_hash, "demo@sleepsense.ai"))
    conn.commit()
    conn.close()

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# ── User operations ───────────────────────────────────────────────────────────
def register_user(username, password, email=""):
    conn = get_db()
    try:
        conn.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                     (username, hash_pw(password), email))
        conn.commit()
        return True, "Account created successfully."
    except sqlite3.IntegrityError:
        return False, "Username already taken."
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE username=? AND password=?",
                       (username, hash_pw(password))).fetchone()
    conn.close()
    return row is not None

def get_user(username):
    conn = get_db()
    row = conn.execute("SELECT id, username, email, created FROM users WHERE username=?",
                       (username,)).fetchone()
    conn.close()
    return dict(row) if row else None

# ── Sleep data operations ─────────────────────────────────────────────────────
def save_sleep_record(username, movement, noise, screen, disorder, score, confidence=0, notes=""):
    conn = get_db()
    conn.execute("""INSERT INTO sleep_data
        (username, movement, noise, screen, predicted_disorder, sleep_score, confidence, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (username, movement, noise, screen, disorder, score, confidence, notes))
    conn.commit()
    conn.close()

def get_user_history(username, limit=50):
    conn = get_db()
    rows = conn.execute("""SELECT * FROM sleep_data WHERE username=?
        ORDER BY recorded_at DESC LIMIT ?""", (username, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_stats(username):
    conn = get_db()
    rows = conn.execute("""SELECT predicted_disorder, sleep_score FROM sleep_data
        WHERE username=? ORDER BY recorded_at DESC LIMIT 30""", (username,)).fetchall()
    conn.close()
    if not rows:
        return {"avg_score": 0, "total": 0, "disorders": {}}
    scores = [r["sleep_score"] for r in rows]
    disorders = {}
    for r in rows:
        d = r["predicted_disorder"]
        disorders[d] = disorders.get(d, 0) + 1
    return {
        "avg_score": round(sum(scores) / len(scores)),
        "total": len(rows),
        "disorders": disorders,
        "best_score": max(scores),
        "worst_score": min(scores)
    }
