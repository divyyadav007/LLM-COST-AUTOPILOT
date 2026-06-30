from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.router_schema import ModelResponse

client = TestClient(app)


def test_api_completions_missing_prompt() -> None:
    """Verifies that empty prompt payloads trigger 400 Bad Request exceptions."""
    response = client.post("/v1/completions", json={"prompt": ""})
    assert response.status_code == 400
    assert "detail" in response.json()


def test_api_completions_invalid_json() -> None:
    """Verifies that missing parameters yield Pydantic 422 ValidationError response payloads."""
    response = client.post("/v1/completions", json={})
    assert response.status_code == 422


@patch("app.services.provider_service.ProviderService.send_request")
def test_api_completions_success(mock_send_request: MagicMock) -> None:
    """Verifies that standard payloads get routed correctly, responding with complexity mapping details."""
    mock_response = ModelResponse(
        provider="groq",
        model_name="llama3-8b",
        output_text="Fast-path routed answer.",
        prompt_tokens=10,
        completion_tokens=10,
        total_cost=0.000001,
        latency_ms=80.0,
    )
    # Configure the patched async send_request method
    mock_send_request.side_effect = AsyncMock(return_value=mock_response)

    response = client.post("/v1/completions", json={"prompt": "What is the capital of France?"})
    assert response.status_code == 200

    json_data = response.json()
    assert json_data["complexity_tier"] in ["simple", "moderate"]
    assert json_data["model_allocated"] in ["llama3-8b", "mistral-7b"]
    assert json_data["completion"] == "Fast-path routed answer."
    assert "routing_confidence" in json_data
    assert "metrics" in json_data
    assert json_data["metrics"]["latency_ms"] == 80.0
