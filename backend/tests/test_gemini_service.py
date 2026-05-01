import anyio
import pytest
from pydantic import BaseModel

from core.config import Settings
from services import gemini_service
from services.gemini_service import GeminiService, GeminiServiceError


class DummyResponse(BaseModel):
    value: str


def make_service() -> GeminiService:
    return GeminiService(
        Settings(
            app_name="test",
            environment="test",
            gemini_api_key="test-key",
            gemini_file_search_store="test-store",
            gemini_file_search_model="primary",
            gemini_file_search_fallback_models=["secondary"],
            gemini_synthesis_model="synthesis",
            gemini_synthesis_fallback_models=[],
            gemini_calls_per_minute=999,
            gemini_min_seconds_between_calls=0,
            allowed_origins=[],
        )
    )


def test_transient_provider_error_tries_fallback_model(monkeypatch) -> None:
    service = make_service()
    calls: list[str] = []

    async def no_sleep(_: float) -> None:
        return None

    def fake_generate_content(model: str, *args, **kwargs):
        calls.append(model)
        if model == "primary":
            raise RuntimeError("503 UNAVAILABLE high demand")
        return DummyResponse(value="ok")

    monkeypatch.setattr(gemini_service.asyncio, "sleep", no_sleep)
    monkeypatch.setattr(service, "_generate_content", fake_generate_content)

    response = anyio.run(
        service._generate_content_with_retries,
        ["primary", "secondary"],
        "prompt",
        DummyResponse,
        None,
        True,
    )

    assert response == DummyResponse(value="ok")
    assert calls == ["primary", "primary", "primary", "secondary"]


def test_all_transient_provider_errors_raise_clear_message(monkeypatch) -> None:
    service = make_service()

    async def no_sleep(_: float) -> None:
        return None

    def fake_generate_content(*args, **kwargs):
        raise RuntimeError("503 UNAVAILABLE high demand")

    monkeypatch.setattr(gemini_service.asyncio, "sleep", no_sleep)
    monkeypatch.setattr(service, "_generate_content", fake_generate_content)

    with pytest.raises(GeminiServiceError, match="temporarily unavailable"):
        anyio.run(
            service._generate_content_with_retries,
            ["primary", "secondary"],
            "prompt",
            DummyResponse,
            None,
            True,
        )
