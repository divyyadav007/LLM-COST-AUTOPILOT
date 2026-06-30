import logging
import os
import time
from typing import Any

import httpx
import tiktoken

from app.schemas.router_schema import ModelResponse

logger = logging.getLogger(__name__)


class ProviderService:
    """Service to handle outbound API requests to LLM providers (Groq, Mistral)."""

    def __init__(self, config_data: dict[str, Any]) -> None:
        """
        Initializes the provider client adapter with YAML configurations.

        Args:
            config_data (Dict[str, Any]): Parsing model mappings and credentials configuration.
        """
        self.config = config_data
        # Standard fallback tokenizer mapping for safe pricing estimation
        try:
            self.fallback_encoder = tiktoken.get_encoding("cl100k_base")
            logger.debug("Successfully loaded cl100k_base tokenizer encoding.")
        except Exception as err:
            logger.warning(
                "Could not load tiktoken cl100k_base encoding: %s. Using whitespace fallback.", err
            )
            self.fallback_encoder = None

    def estimate_token_count(self, text: str) -> int:
        """
        Calculates mathematical token footprint using first-principle BPE encoding.

        Args:
            text (str): Inbound string value.

        Returns:
            int: Token estimate.
        """
        if not text:
            return 0
        if self.fallback_encoder:
            try:
                return len(self.fallback_encoder.encode(text, disallowed_special=()))
            except Exception as encode_err:
                logger.debug(
                    "Tiktoken encoding failed: %s. Falling back to heuristic count.", encode_err
                )
        return len(text.split()) * 13 // 10  # standard 1.3 tokens-per-word heuristic

    async def send_request(self, prompt: str, internal_model_name: str) -> ModelResponse:
        """
        Executes fully async network I/O call towards the targeted model infrastructure.

        Args:
            prompt (str): Text query for the model.
            internal_model_name (str): Internal model registry handle.

        Returns:
            ModelResponse: Unified model response metrics and text content.
        """
        model_meta = self.config["models"].get(internal_model_name)
        if not model_meta:
            logger.error("Target model %s not found in config", internal_model_name)
            raise ValueError(
                f"Target model meta {internal_model_name} not existing in system registry configuration maps."
            )

        provider_name = model_meta["provider"]
        provider_meta = self.config["providers"][provider_name]

        # Pull API token validation safely out of the process environment contexts
        api_key = os.getenv(provider_meta["api_key_env"])
        if not api_key:
            logger.warning(
                "API Key %s not set in environment. Falling back to mock mock_key.",
                provider_meta["api_key_env"],
            )
            api_key = "MOCK_KEY_DEVELOPMENT_PURPOSE"

        # Calculate Input weight profiles
        prompt_tokens = self.estimate_token_count(prompt)

        # Build strict payload mapping complying with OpenAI standardized schemas
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        payload = {
            "model": model_meta["model_id"],
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
        }

        url = f"{provider_meta['base_url']}/chat/completions"
        start_time = time.perf_counter()

        logger.info("Sending async POST request to provider %s at URL %s", provider_name, url)
        # Asynchronous context protocol implementation avoiding thread blocking states
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                response_json = response.json()
        except Exception as http_err:
            logger.error(
                "Southbound API network error on %s: %s", provider_name, http_err, exc_info=True
            )
            raise

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

        logger.info(
            "Successfully fetched response. Cost: $%.6f, Latency: %.2fms",
            total_transaction_cost,
            latency_ms,
        )

        return ModelResponse(
            provider=provider_name,
            model_name=internal_model_name,
            output_text=output_text,
            prompt_tokens=actual_prompt_tokens,
            completion_tokens=completion_tokens,
            total_cost=total_transaction_cost,
            latency_ms=latency_ms,
        )
