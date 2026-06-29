import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "farmchain.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS farmers (
                wallet_address TEXT PRIMARY KEY,
                name           TEXT NOT NULL,
                farm_name      TEXT NOT NULL,
                location       TEXT NOT NULL,
                certification  TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS batches (
                batch_id        TEXT PRIMARY KEY,
                farmer_wallet   TEXT NOT NULL,
                crop_name       TEXT NOT NULL,
                harvest_date    TEXT NOT NULL,
                is_organic      INTEGER NOT NULL,
                quantity_kg     REAL NOT NULL,
                notes           TEXT DEFAULT '',
                tamper_detected INTEGER DEFAULT 0,
                suspended       INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS handlers (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id  TEXT NOT NULL,
                handler   TEXT NOT NULL,
                location  TEXT NOT NULL,
                tamper    INTEGER NOT NULL,
                timestamp TEXT,
                FOREIGN KEY (batch_id) REFERENCES batches(batch_id)
            );
            CREATE TABLE IF NOT EXISTS fraud_reports (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id      TEXT NOT NULL,
                consumer_id   TEXT,
                reason        TEXT NOT NULL,
                created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        try:
            conn.execute("ALTER TABLE batches ADD COLUMN suspended INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass
