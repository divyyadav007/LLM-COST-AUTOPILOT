from unittest.mock import AsyncMock, MagicMock

import pytest

from app.schemas.router_schema import ModelResponse
from app.services.evaluator_service import EvaluatorService


@pytest.mark.asyncio
async def test_evaluator_verify_quality_success() -> None:
    """Verifies that evaluator parses judge JSON and issues correct quality audit reports."""
    provider_mock = MagicMock()

    gold_resp = ModelResponse(
        provider="mistral",
        model_name="mistral-7b",
        output_text="Gold ground truth answer.",
        prompt_tokens=5,
        completion_tokens=5,
        total_cost=0.0000025,
        latency_ms=100.0,
    )

    judge_resp = ModelResponse(
        provider="mistral",
        model_name="mistral-7b",
        output_text='```json\n{\n  "score": 85,\n  "reason": "High quality response"\n}\n```',
        prompt_tokens=50,
        completion_tokens=20,
        total_cost=0.0000175,
        latency_ms=200.0,
    )

    provider_mock.send_request = AsyncMock()
    provider_mock.send_request.side_effect = [gold_resp, judge_resp]

    evaluator = EvaluatorService(provider_service=provider_mock, gold_standard_model="mistral-7b")
    report = await evaluator.verify_quality_async("Hello", "Cheap response")

    assert report["status"] == "SUCCESS"
    assert report["quality_score"] == 85.0
    assert report["escalate_flag"] is False
    assert report["reason"] == "High quality response"
    assert report["gold_cost_incurred"] == gold_resp.total_cost + judge_resp.total_cost


@pytest.mark.asyncio
async def test_evaluator_verify_quality_escalate() -> None:
    """Verifies that scores under 80% trigger escalation flags."""
    provider_mock = MagicMock()

    gold_resp = ModelResponse(
        provider="mistral",
        model_name="mistral-7b",
        output_text="Gold ground truth answer.",
        prompt_tokens=5,
        completion_tokens=5,
        total_cost=0.0000025,
        latency_ms=100.0,
    )

    judge_resp = ModelResponse(
        provider="mistral",
        model_name="mistral-7b",
        output_text='```json\n{\n  "score": 72,\n  "reason": "Fails details"\n}\n```',
        prompt_tokens=50,
        completion_tokens=20,
        total_cost=0.0000175,
        latency_ms=200.0,
    )

    provider_mock.send_request = AsyncMock()
    provider_mock.send_request.side_effect = [gold_resp, judge_resp]

    evaluator = EvaluatorService(provider_service=provider_mock, gold_standard_model="mistral-7b")
    report = await evaluator.verify_quality_async("Hello", "Cheap response")

    assert report["status"] == "SUCCESS"
    assert report["quality_score"] == 72.0
    assert report["escalate_flag"] is True
