import os
import time
import httpx
import tiktoken
from typing import Dict, Any
from app.schemas.router_schema import ModelResponse

class ProviderService:
    def __init__(self, config_data: Dict[str, Any]):
        """
        Registry mapping aur client configurations initialization loop.
        """
        self.config = config_data
        # Standard fallback tokenizer mapping for safe pricing estimation
        try:
            self.fallback_encoder = tiktoken.get_encoding("cl100k_base")
        except Exception:
            self.fallback_encoder = None

    def estimate_token_count(self, text: str) -> int:
        """
        Calculates mathematical token footprint using first-principle BPE encoding.
        """
        if not text:
            return 0
        if self.fallback_encoder:
            return len(self.fallback_encoder.encode(text, disallowed_special=()))
        return len(text.split()) // 4  # Standard heuristics fallback rule

    async def send_request(self, prompt: str, internal_model_name: str) -> ModelResponse:
        """
        Executes fully async network I/O call towards the targeted model infrastructure.
        """
        model_meta = self.config["models"].get(internal_model_name)
        if not model_meta:
            raise ValueError(f"Target model meta {internal_model_name} not existing in system registry configuration maps.")

        provider_name = model_meta["provider"]
        provider_meta = self.config["providers"][provider_name]
        
        # Pull API token validation safely out of the process environment contexts
        api_key = os.getenv(provider_meta["api_key_env"], "MOCK_KEY_DEVELOPMENT_PURPOSE")
        
        # Calculate Input weight profiles
        prompt_tokens = self.estimate_token_count(prompt)
        
        # Build strict payload mapping complying with OpenAI standardized schemas
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model_meta["model_id"],
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
        }

        url = f"{provider_meta['base_url']}/chat/completions"
        start_time = time.perf_counter()

        # Asynchronous context protocol implementation avoiding thread blocking states
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            response_json = response.json()

        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000.0

        # Output extraction and mathematical normalization metrics mappings
        output_text = response_json["choices"][0]["message"]["content"]
        
        # Upstream actual token payload metadata values tracking
        usage = response_json.get("usage", {})
        completion_tokens = usage.get("completion_tokens", self.estimate_token_count(output_text))
        actual_prompt_tokens = usage.get("prompt_tokens", prompt_tokens)

        # Cost calculation formulation: (Tokens * Cost_Per_Token) / 1,000,000
        input_cost = (actual_prompt_tokens * model_meta["input_cost_per_m"]) / 1_000_000.0
        output_cost = (completion_tokens * model_meta["output_cost_per_m"]) / 1_000_000.0
        total_transaction_cost = input_cost + output_cost

        return ModelResponse(
            provider=provider_name,
            model_name=internal_model_name,
            output_text=output_text,
            prompt_tokens=actual_prompt_tokens,
            completion_tokens=completion_tokens,
            total_cost=total_transaction_cost,
            latency_ms=latency_ms
        )