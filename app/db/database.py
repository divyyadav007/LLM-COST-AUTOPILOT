import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "autopilot.db")

def get_db_connection():
    """
    Establishes and configures thread connection protocols with SQLite backend.
    """
    conn = sqlite3.connect(DB_PATH)
    # Enable associative dictionary rows instead of raw tuple indices
    conn.row_factory = sqlite3.Row
    return conn

def init_db_infrastructure():
    """
    Executes table configuration syntax mapping audit logs telemetry properties.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        prompt TEXT,
        predicted_tier TEXT,
        routed_model TEXT,
        prompt_tokens INTEGER,
        completion_tokens INTEGER,
        actual_cost REAL,
        baseline_premium_cost REAL,
        latency_ms REAL,
        quality_score REAL DEFAULT NULL,
        escalate_flag INTEGER DEFAULT 0,
        eval_reason TEXT DEFAULT NULL
    )
    """)
    conn.commit()
    conn.close()