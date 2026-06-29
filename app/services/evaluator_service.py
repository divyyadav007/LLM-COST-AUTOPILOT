import json
import re
from typing import Dict, Any
from app.services.provider_service import ProviderService

class EvaluatorService:
    def __init__(self, provider_service: ProviderService, gold_standard_model: str = "mistral-7b"):
        """
        Evaluator engine ka constructor jo hamari base provider service aur
        benchmark high-tier model standard ko dependency inject karta hai.
        """
        self.provider = provider_service
        self.gold_model = gold_standard_model

    async def verify_quality_async(self, prompt: str, cheap_model_output: str) -> Dict[str, Any]:
        """
        Background worker engine: Ye cheap model ke output ko gold standard model
        ke response se compare karke quality score generate karta hai.
        """
        # Step 1: Sabse pehle gold standard model (Ground Truth) se same prompt par output fetch karo
        try:
            gold_response = await self.provider.send_request(prompt, self.gold_model)
            gold_text = gold_response.output_text
        except Exception as provider_err:
            return {
                "status": "EVAL_FAILED",
                "reason": f"Gold benchmark endpoint target down: {provider_err}",
                "quality_score": 0.0,
                "escalate_flag": True,
                "gold_cost_incurred": 0.0
            }

        # Step 2: System Evaluation Prompt Design (LLM-as-a-Judge Protocol)
        eval_prompt = f"""You are an expert Production AI Quality Audit Engine. Your task is to evaluate the quality of a CHEAP model's response against a high-tier GOLD STANDARD response.

    USER ORIGINAL PROMPT:
    \"\"\"{prompt}\"\"\"

    GOLD STANDARD RESPONSE (Ground Truth):
    \"\"\"{gold_text}\"\"\"

    CHEAP MODEL RESPONSE (Under Review):
    \"\"\"{cheap_model_output}\"\"\"

    Analyze factual alignment, accuracy, and completeness. You MUST respond strictly with a valid JSON block enclosed in markdown code fences, containing exactly two keys: 'score' (an integer from 0 to 100) and 'reason' (a short engineering explanation).

    Example Output Format:
    ```json
    {{
      "score": 90,
      "reason": "Captures the main architectural features perfectly, missing minor details."
    }}
    ```
    """
        # Step 3: Judge Call and Bulletproof Parsing Engine
        try:
            eval_response = await self.provider.send_request(eval_prompt, self.gold_model)
            eval_text = eval_response.output_text
            # Robust JSON extraction via regex pattern matching
            # Open-source models like Mistral can add conversational padding before/after JSON codeblocks.
            json_match = re.search(r"```json\s*(\{.*?\})\s*```", eval_text, re.DOTALL)
            
            if json_match:
                parsed_metrics = json.loads(json_match.group(1))
            else:
                # Fallback: code fences na ho toh complete text block ko extract karo
                parsed_metrics = json.loads(eval_text.strip())

            score = float(parsed_metrics.get("score", 50.0))
            reason = parsed_metrics.get("reason", "Fails to present structured logs format evaluation.")

            # Decision Matrix Rule: Agar score 80.0 se niche gira, toh automatic system data drift trigger karo
            escalate_flag = score < 80.0

            return {
                "status": "SUCCESS",
                "quality_score": score,
                "reason": reason,
                "escalate_flag": escalate_flag,
                "gold_cost_incurred": gold_response.total_cost + eval_response.total_cost
            }

        except Exception as eval_parse_err:
            return {
                "status": "PARSING_ANOMALY",
                "reason": f"LLM-as-a-judge formatting deviation: {eval_parse_err}. Raw Text: {eval_text[:100]}",
                "quality_score": 0.0,
                "escalate_flag": True,
                "gold_cost_incurred": 0.0
            }