import logging
from typing import Any

from app.db.database import get_db_connection

logger = logging.getLogger(__name__)


def insert_audit_entry(log_data: dict[str, Any]) -> None:
    """
    Saves a transactional metadata record inside the auditing SQLite table.

    Args:
        log_data (Dict[str, Any]): Dictionary containing transaction details.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO audit_logs (
            prompt, predicted_tier, routed_model, prompt_tokens, 
            completion_tokens, actual_cost, baseline_premium_cost, 
            latency_ms, quality_score, escalate_flag, eval_reason
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        cursor.execute(
            query,
            (
                log_data["prompt"],
                log_data["predicted_tier"],
                log_data["routed_model"],
                log_data["prompt_tokens"],
                log_data["completion_tokens"],
                log_data["actual_cost"],
                log_data["baseline_premium_cost"],
                log_data["latency_ms"],
                log_data.get("quality_score"),
                1 if log_data.get("escalate_flag") else 0,
                log_data.get("eval_reason"),
            ),
        )

        conn.commit()
        conn.close()
        logger.debug(
            "Successfully inserted audit log for routed model: %s", log_data["routed_model"]
        )
    except Exception as err:
        logger.error("Failed to insert audit log: %s", err, exc_info=True)
        raise


def pull_analytical_aggregates() -> dict[str, Any]:
    """
    Computes high-intent business summary metrics from the audit logs.

    Returns:
        Dict[str, Any]: Metrics including total requests, total costs, saved delta, etc.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                COUNT(id) as total_calls,
                SUM(actual_cost) as total_spent,
                SUM(baseline_premium_cost) as total_baseline,
                AVG(latency_ms) as avg_latency,
                AVG(quality_score) as avg_quality,
                SUM(escalate_flag) as total_escalations
            FROM audit_logs
        """)

        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else {}
    except Exception as err:
        logger.error("Failed to fetch analytical aggregates: %s", err, exc_info=True)
        return {}
