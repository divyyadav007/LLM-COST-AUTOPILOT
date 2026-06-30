import logging
import os
import sqlite3

from app.core.config import settings

logger = logging.getLogger(__name__)


def get_db_connection() -> sqlite3.Connection:
    """
    Establishes and configures thread connection protocols with SQLite backend.

    Returns:
        sqlite3.Connection: A sqlite3 connection with sqlite3.Row configured.
    """
    conn = sqlite3.connect(settings.DB_PATH)
    # Enable associative dictionary rows instead of raw tuple indices
    conn.row_factory = sqlite3.Row
    return conn


def init_db_infrastructure() -> None:
    """
    Executes table configuration syntax mapping audit logs telemetry properties.
    """
    logger.info("Initializing database infrastructure at %s", settings.DB_PATH)
    # Ensure parent directories exist
    os.makedirs(os.path.dirname(settings.DB_PATH), exist_ok=True)

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
    logger.info("Database infrastructure initialized successfully.")
