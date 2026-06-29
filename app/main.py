import os
import yaml
from typing import Any  # FIX: Explicit type hint validation added
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from app.services.provider_service import ProviderService
from app.services.classifier_service import ClassifierService
from app.services.evaluator_service import EvaluatorService
from app.db.database import init_db_infrastructure
from app.db.models import insert_audit_entry

load_dotenv()

app = FastAPI(title="LLM Cost Autopilot Gateway", version="1.0.0")

# Setup system configuration mappings matrix definitions
config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "routing_config.yaml")
with open(config_path, "r") as file:
    config_data = yaml.safe_load(file)

init_db_infrastructure()
classifier = ClassifierService()
provider_client = ProviderService(config_data=config_data)
evaluator = EvaluatorService(provider_service=provider_client, gold_standard_model="mistral-7b")

class CompletionRequest(BaseModel):
    prompt: str

async def execute_background_audit_loop(prompt: str, output_text: str, routed_model: str, response_meta: Any):
    """
    Decoupled task queue worker executing evaluations and telemetry database commits.
    """
    eval_report = await evaluator.verify_quality_async(prompt, output_text)
    
    # Financial aggregate projections calculation tracking formulas
    baseline_input_fees = (response_meta.prompt_tokens * 0.25) / 1_000_000.0
    baseline_output_fees = (response_meta.completion_tokens * 0.25) / 1_000_000.0
    baseline_total_calculated = baseline_input_fees + baseline_output_fees

    audit_log_payload = {
        "prompt": prompt,
        "predicted_tier": config_data["models"][routed_model]["tier"],
        "routed_model": routed_model,
        "prompt_tokens": response_meta.prompt_tokens,
        "completion_tokens": response_meta.completion_tokens,
        "actual_cost": response_meta.total_cost,
        "baseline_premium_cost": baseline_total_calculated,
        "latency_ms": response_meta.latency_ms,
        "quality_score": eval_report.get("quality_score", 100.0) if eval_report["status"] == "SUCCESS" else None,
        "escalate_flag": eval_report.get("escalate_flag", False),
        "eval_reason": eval_report.get("reason", "None")
    }
    insert_audit_entry(audit_log_payload)

@app.post("/v1/completions")
async def route_completion_request(payload: CompletionRequest, background_tasks: BackgroundTasks):
    """
    High-performance async router gateway abstraction proxy handling enterprise prompts.
    """
    if not payload.prompt:
        raise HTTPException(status_code=400, detail="Prompt context variable tokens cannot be blank strings.")
        
    assigned_tier, confidence = classifier.predict_tier(payload.prompt)
    routed_model = config_data["tier_model_mapping"][assigned_tier]
    
    try:
        # Fast path delivery handling - routed directly to target provider allocation loop
        response_data = await provider_client.send_request(payload.prompt, routed_model)
        
        # Enqueue background telemetry auditing completely out of user wait-time threads
        background_tasks.add_task(
            execute_background_audit_loop, 
            payload.prompt, 
            response_data.output_text, 
            routed_model, 
            response_data
        )
        
        return {
            "model_allocated": routed_model,
            "routing_confidence": confidence,
            "complexity_tier": assigned_tier,
            "completion": response_data.output_text,
            "metrics": {
                "latency_ms": response_data.latency_ms,
                "transaction_cost_usd": response_data.total_cost
            }
        }
    except Exception as api_err:
        raise HTTPException(status_code=500, detail=f"Southbound network connection adapter failure: {api_err}")
async def runtime_production_simulation_pipeline():
    # Initialize DB architecture components
    init_db_infrastructure()

    # Load system configurations parameters mapping tables
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "routing_config.yaml")
    with open(config_path, "r") as file:
        config_data = yaml.safe_load(file)

    # Instantiate system core automation layer pools
    classifier = ClassifierService()
    provider_client = ProviderService(config_data=config_data)
    evaluator = EvaluatorService(provider_service=provider_client, gold_standard_model="mistral-7b")

    print("\n=======================================================")
    print("--- AUTOPILOT GATEWAY V4: COMPLETE PERSISTENCE TRAIL ---")
    print("=======================================================\n")

    # High complexity token density prompts structure mapping
    simulation_prompts = [
        "Give me a 5 word text validation keyword array",
        "Summarize the technical infrastructure requirements blueprint of modular orchestration patterns across clusters",
        "Analyze this execution breakdown and trace the exact regular expressions causing thread blocks"
    ]

    for user_prompt in simulation_prompts:
        print(f"-----------------------------------------------------------")
        print(f"[ENTRY LOG] Ingesting prompt query: '{user_prompt}'")
        
        # 1. Routing Layer Classification choice choices
        assigned_tier, confidence = classifier.predict_tier(user_prompt)
        routed_model = config_data["tier_model_mapping"][assigned_tier]
        
        # 2. Fire cheap fast-track model response path
        try:
            # Running response pipeline on actual endpoint
            response = await provider_client.send_request(user_prompt, routed_model)
            
            # 3. Fire immediate synchronous evaluation pipeline for current validation trace simulation
            print("[BACKGROUND SYSTEM] Compiling quality parity matrices metrics...")
            eval_report = await evaluator.verify_quality_async(
                prompt=user_prompt,
                cheap_model_output=response.output_text
            )

            # Heuristic analysis to compare baseline parameters if everything was passed onto Premium Model directly
            # Assumption model cost tracking calculation: premium model is mistral-7b costing 0.25 input / 0.25 output per M
            baseline_input_fees = (response.prompt_tokens * 0.25) / 1_000_000.0
            baseline_output_fees = (response.completion_tokens * 0.25) / 1_000_000.0
            baseline_total_calculated = baseline_input_fees + baseline_output_fees

            # 4. Consolidate full payload dictionary allocation mapping for logging sink database actions
            audit_log_payload = {
                "prompt": user_prompt,
                "predicted_tier": assigned_tier,
                "routed_model": routed_model,
                "prompt_tokens": response.prompt_tokens,
                "completion_tokens": response.completion_tokens,
                "actual_cost": response.total_cost,
                "baseline_premium_cost": baseline_total_calculated,
                "latency_ms": response.latency_ms,
                "quality_score": eval_report.get("quality_score", 100.0) if eval_report["status"] == "SUCCESS" else None,
                "escalate_flag": eval_report.get("escalate_flag", False),
                "eval_reason": eval_report.get("reason", "None")
            }

            # Commit trail row inside our persistence schema layers
            insert_audit_entry(audit_log_payload)
            print("[DATABASE LOG] Transaction record committed successfully to SQLite schema arrays.")

        except Exception as runtime_anomaly:
            print(f" [ALERT EXCEPTION ERROR] Telemetry collection pipeline bypassed entry hook: {runtime_anomaly}")

    # 5. Extract system financial dashboard analytics logs matrix
    metrics_summary = pull_analytical_aggregates()
    print(f"\n=========================================================")
    print(f"--- PILOT ROI DASHBOARD TELEMETRY BATCH AGGREGATION ---")
    print(f"=========================================================")
    print(f" * Total Request Packets Tracked: {metrics_summary.get('total_calls')}")
    print(f" * Accumulated Router API Incurred Cost: ${metrics_summary.get('total_spent', 0.0):.6f}")
    print(f" * Pure Baseline Premium Expense Projection: ${metrics_summary.get('total_baseline', 0.0):.6f}")
    
    # Mathematical calculation tracking cost savings metrics margins percentage
    total_baseline = metrics_summary.get('total_baseline', 0.0) if metrics_summary.get('total_baseline') is not None else 0.0
    total_spent = metrics_summary.get('total_spent', 0.0) if metrics_summary.get('total_spent') is not None else 0.0
    
    saved_delta = max(0.0, total_baseline - total_spent)
    savings_pct = (saved_delta / total_baseline) * 100.0 if total_baseline > 0 else 0.0
    
    # Fix Null values for Average Latency and Quality calculations safely
    avg_latency = metrics_summary.get('avg_latency', 0.0) if metrics_summary.get('avg_latency') is not None else 0.0
    avg_quality = metrics_summary.get('avg_quality', 0.0) if metrics_summary.get('avg_quality') is not None else 0.0
    
    print(f" * NET TRANSACTIONAL DOLLARS SAVED: ${saved_delta:.6f}")
    print(f" * ULTIMATE ENTERPRISE COST REDUCTION MARGIN: {savings_pct:.2f}%")
    print(f" * Average Pipeline Latency: {avg_latency:.2f}ms")
    print(f" * Parity Quality Performance Baseline: {avg_quality:.1f}/100")
    print(f"=========================================================\n")

if __name__ == "__main__":
    asyncio.run(runtime_production_simulation_pipeline())