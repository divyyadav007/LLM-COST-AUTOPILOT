import streamlit as st
import pandas as pd
import sqlite3
import os

st.set_page_config(layout="wide")
st.title("📊 LLM Cost Autopilot Telemetry Center")
st.markdown("### Real-Time Financial ROI Monitoring & Model Performance Insights")

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "db", "autopilot.db")

def load_historical_metrics_frame():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM audit_logs ORDER BY timestamp DESC", conn)
    conn.close()
    return df

df = load_historical_metrics_frame()

if df.empty:
    st.warning("No operational log metrics found inside system registry data tables yet. Send API traffic to aggregate values graphs.")
else:
    # Top Level KPI Row Allocation Mapping Structures
    total_calls = len(df)
    total_spent = df["actual_cost"].sum()
    total_baseline = df["baseline_premium_cost"].sum()
    net_savings = max(0.0, total_baseline - total_spent)
    savings_percentage = (net_savings / total_baseline) * 100.0 if total_baseline > 0 else 0.0
    avg_quality = df["quality_score"].mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="Total Routed Requests", value=f"{total_calls} Packets")
    col2.metric(label="Total Accumulated Cost Incurred", value=f"${total_spent:.4f}")
    
    # Financial Highlight Metrics Card Logic
    col3.metric(
        label="NET Capital Dollars Saved ($)", 
        value=f"${net_savings:.4f}", 
        delta=f"{savings_percentage:.1f}% Expense Down"
    )
    col4.metric(label="System Quality Parity Baseline", value=f"{avg_quality:.1f}/100")

    st.markdown("---")
    
    # Interactive Data Section Tables
    st.subheader("📋 Core Audit Logs Registry Database")
    st.dataframe(
        df[["timestamp", "predicted_tier", "routed_model", "prompt_tokens", "completion_tokens", "actual_cost", "quality_score", "escalate_flag"]],
        use_container_width=True
    )