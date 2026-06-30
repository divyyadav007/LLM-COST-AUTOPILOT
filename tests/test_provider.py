from unittest.mock import AsyncMock, patch

import pytest

from app.schemas.router_schema import ModelResponse
from app.services.provider_service import ProviderService


def test_token_estimation() -> None:
    """Verifies that token count estimation falls back gracefully when tiktoken isn't available."""
    config = {"providers": {}, "models": {}}
    provider = ProviderService(config_data=config)
    assert provider.estimate_token_count("") == 0
    assert provider.estimate_token_count("Hello, world!") > 0


@pytest.mark.asyncio
async def test_send_request_mock() -> None:
    """Verifies that send_request processes provider responses, token tracking, and costing formulas."""
    config = {
        "providers": {
            "groq": {"base_url": "https://api.groq.com/openai/v1", "api_key_env": "GROQ_API_KEY"}
        },
        "models": {
            "llama3-8b": {
                "provider": "groq",
                "model_id": "llama-3.1-8b-instant",
                "input_cost_per_m": 0.05,
                "output_cost_per_m": 0.08,
                "tier": "simple",
            }
        },
    }
    provider = ProviderService(config_data=config)

    mock_json_payload = {
        "choices": [{"message": {"content": "Mock completion response."}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 15},
    }

    with patch("httpx.AsyncClient.post") as mock_post:
        # Configure the mock response
        mock_resp = AsyncMock()
        mock_resp.status_code = 200
        mock_resp.json = lambda: mock_json_payload
        mock_resp.raise_for_status = lambda: None
        mock_post.return_value = mock_resp

        response = await provider.send_request("Hello classifier", "llama3-8b")

        assert isinstance(response, ModelResponse)
        assert response.provider == "groq"
        assert response.model_name == "llama3-8b"
        assert response.output_text == "Mock completion response."
        assert response.prompt_tokens == 10
        assert response.completion_tokens == 15

        # Math verification: (10 * 0.05 + 15 * 0.08) / 1_000_000 = (0.5 + 1.2) / 1_000_000 = 1.7 / 1_000_000 = 0.0000017
        assert abs(response.total_cost - 0.0000017) < 1e-9
