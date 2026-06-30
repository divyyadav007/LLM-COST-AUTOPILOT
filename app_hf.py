import asyncio
import os
import sqlite3

import pandas as pd
import streamlit as st
import yaml
from dotenv import load_dotenv

from app.services.classifier_service import ClassifierService
from app.services.evaluator_service import EvaluatorService
from app.services.provider_service import ProviderService

# Load environment variables
load_dotenv()

st.set_page_config(layout="wide", page_title="LLM Cost Autopilot Gateway")

# --- 1. CONFIGURATION & INFRASTRUCTURE FACTORY INITIALIZATION ---
from app.core.config import settings
from app.db.database import init_db_infrastructure
from app.db.models import insert_audit_entry

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config", "routing_config.yaml")
DB_PATH = settings.DB_PATH

# Initialize table structure if absent
init_db_infrastructure()

with open(CONFIG_PATH) as file:
    config_data = yaml.safe_load(file)

# Instantiate background prediction clusters
classifier = ClassifierService()
provider_client = ProviderService(config_data=config_data)
evaluator = EvaluatorService(provider_service=provider_client, gold_standard_model="mistral-7b")

# --- 2. PIPELINE INTERFACE LAYER ---
st.title("🚀 LLM Cost Autopilot Gateway")
st.markdown(
    "### Production-Grade Cost Optimization Routing Layer with Async Quality Verification Loops"
)

# Sidebar Manual User Simulation Tool Context
st.sidebar.header("🕹️ Gateway Live Proxy Client")
user_input = st.sidebar.text_area(
    "Ingest Payload User Prompt Query:", placeholder="Type your text task constraints here..."
)
fire_route = st.sidebar.button("Dispatch API Completion Packet")

if fire_route and user_input:
    with st.spinner("Processing gateway complexity mapping optimization algorithms..."):
        # Runtime prediction loop
        assigned_tier, target_confidence = classifier.predict_tier(user_input)
        routed_model_internal = config_data["tier_model_mapping"][assigned_tier]

        # Dispatch execution through unified non-blocking adapter loop safely
        try:
            # Re-routing model targets matching pricing thresholds table matrices
            response_payload = asyncio.run(
                provider_client.send_request(user_input, routed_model_internal)
            )

            # Synchronous simulation execution loop tracking quality parity indices inside sandbox dashboard
            eval_report = asyncio.run(
                evaluator.verify_quality_async(user_input, response_payload.output_text)
            )

            # Baseline pricing metrics verification formulas formulation
            baseline_input_fees = (response_payload.prompt_tokens * 0.25) / 1_000_000.0
            baseline_output_fees = (response_payload.completion_tokens * 0.25) / 1_000_000.0
            baseline_total_projected = baseline_input_fees + baseline_output_fees

            # Persist transaction logs using models
            audit_payload = {
                "prompt": user_input,
                "predicted_tier": assigned_tier,
                "routed_model": routed_model_internal,
                "prompt_tokens": response_payload.prompt_tokens,
                "completion_tokens": response_payload.completion_tokens,
                "actual_cost": response_payload.total_cost,
                "baseline_premium_cost": baseline_total_projected,
                "latency_ms": response_payload.latency_ms,
                "quality_score": (
                    eval_report.get("quality_score", 100.0)
                    if eval_report["status"] == "SUCCESS"
                    else None
                ),
                "escalate_flag": eval_report.get("escalate_flag", False),
                "eval_reason": eval_report.get("reason", "None"),
            }
            insert_audit_entry(audit_payload)
            st.sidebar.success("Transaction Committed successfully!")

        except Exception as api_route_err:
            st.sidebar.error(f"Gateway Adapter Exception thrown: {api_route_err}")


# --- 3. ANALYTICS OBSERVABILITY LAYER ---
def load_historical_ledger():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM audit_logs ORDER BY id DESC", conn)
    conn.close()
    return df


df_logs = load_historical_ledger()

if not df_logs.empty:
    # Calculate real mathematical business ROI counters definitions
    total_actual_spend = df_logs["actual_cost"].sum()
    total_baseline_projected = df_logs["baseline_premium_cost"].sum()
    net_dollar_savings = total_baseline_projected - total_actual_spend
    savings_percentage = (
        (net_dollar_savings / total_baseline_projected) * 100.0
        if total_baseline_projected > 0
        else 0.0
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total API Requests Serviced", f"{len(df_logs)} Packets")
    col2.metric("Total Cloud Spend Actual", f"${total_actual_spend:.5f}")
    col3.metric(
        "Net Financial Capital Saved",
        f"${net_dollar_savings:.5f}",
        delta=f"{savings_percentage:.1f}% Savings Plan",
    )
    col4.metric("Mean System Latency Timing", f"{df_logs['latency_ms'].mean():.2f}ms")

    st.markdown("---")
    st.markdown("### 📋 System Audit Trails Ledger Analytics Logs")
    st.dataframe(df_logs, use_container_width=True)
else:
    st.info(
        "💡 Registry database empty. Use the sidebar input tool to throw transactions and build telemetry data loops graphs."
    )
