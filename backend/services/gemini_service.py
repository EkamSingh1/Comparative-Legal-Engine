from __future__ import annotations

import asyncio
import json
from functools import lru_cache
from typing import Any, TypeVar

import anyio
from pydantic import BaseModel, ValidationError

from core.config import Settings, get_settings
from core.limiter import ProviderRateLimiter
from core.prompts import (
    METHODOLOGIES,
    SCHOOL_NAMES,
    build_school_prompt,
    build_synthesis_prompt,
)
from schemas import (
    DISCLAIMER,
    SCHOOL_OUTPUT_MODELS,
    AnalysisResponse,
    Evidence,
    LegalReasoning,
    SchoolAnalysis,
    SchoolKey,
    SynthesisOutput,
)

try:
    from google import genai
    from google.genai import types
except ImportError:  # pragma: no cover - exercised only when deps are not installed.
    genai = None
    types = None


T = TypeVar("T", bound=BaseModel)


class GeminiServiceError(RuntimeError):
    pass


class GeminiService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._store_name: str | None = None
        self._limiter = ProviderRateLimiter(
            calls_per_minute=settings.gemini_calls_per_minute,
            min_spacing_seconds=settings.gemini_min_seconds_between_calls,
        )
        self._client = None

    @property
    def client(self):
        if not self.settings.gemini_api_key:
            raise GeminiServiceError("GEMINI_API_KEY is not configured.")
        if genai is None or types is None:
            raise GeminiServiceError(
                "google-genai is not installed. Install backend/requirements.txt first."
            )
        if self._client is None:
            self._client = genai.Client(api_key=self.settings.gemini_api_key)
        return self._client

    async def analyze(self, scenario: str) -> AnalysisResponse:
        school_results: list[SchoolAnalysis] = []
        raw_outputs: dict[str, Any] = {}

        for school in SchoolKey:
            model_cls = SCHOOL_OUTPUT_MODELS[school]
            output = await self._generate_with_file_search(
                school=school,
                scenario=scenario,
                response_model=model_cls,
            )
            raw_outputs[school.value] = output.model_dump()
            school_results.append(self._to_school_analysis(school, output))

        synthesis = await self._generate_synthesis(scenario, raw_outputs)
        return AnalysisResponse(
            scenario=scenario,
            disclaimer=DISCLAIMER,
            synthesis=synthesis,
            schools=school_results,
        )

    async def _generate_with_file_search(
        self, school: SchoolKey, scenario: str, response_model: type[T]
    ) -> T:
        prompt = build_school_prompt(school, scenario)
        store_name = await self._get_store_name()

        async def call_provider(use_schema: bool) -> T:
            response = await self._generate_content_with_retries(
                model=self.settings.gemini_file_search_model,
                prompt=prompt,
                response_model=response_model,
                store_name=store_name,
                use_schema=use_schema,
            )
            return self._parse_response(response, response_model)

        try:
            return await call_provider(use_schema=True)
        except Exception as exc:
            if not self._looks_like_schema_tool_error(exc):
                raise GeminiServiceError(
                    f"{SCHOOL_NAMES[school]} analysis failed: {exc}"
                ) from exc
            retry_prompt = (
                f"{prompt}\n\nThe provider rejected tool structured-output mode. "
                "Still return a single valid JSON object matching the schema exactly."
            )
            prompt = retry_prompt
            try:
                return await call_provider(use_schema=False)
            except Exception as retry_exc:
                raise GeminiServiceError(
                    f"{SCHOOL_NAMES[school]} analysis failed after retry: {retry_exc}"
                ) from retry_exc

    async def _generate_synthesis(
        self, scenario: str, raw_outputs: dict[str, Any]
    ) -> SynthesisOutput:
        prompt = build_synthesis_prompt(scenario, json.dumps(raw_outputs, indent=2))
        response = await self._generate_content_with_retries(
            model=self.settings.gemini_synthesis_model,
            prompt=prompt,
            response_model=SynthesisOutput,
            store_name=None,
            use_schema=True,
        )
        try:
            return self._parse_response(response, SynthesisOutput)
        except Exception as exc:
            raise GeminiServiceError(f"Synthesis failed: {exc}") from exc

    def _generate_content(
        self,
        model: str,
        prompt: str,
        response_model: type[BaseModel],
        store_name: str | None,
        use_schema: bool,
    ):
        config_kwargs: dict[str, Any] = {
            "temperature": 0.2,
            "response_mime_type": "application/json",
        }
        if use_schema:
            config_kwargs["response_json_schema"] = response_model.model_json_schema()
        if store_name:
            config_kwargs["tools"] = [
                types.Tool(
                    file_search=types.FileSearch(file_search_store_names=[store_name])
                )
            ]

        return self.client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(**config_kwargs),
        )

    async def _generate_content_with_retries(
        self,
        model: str,
        prompt: str,
        response_model: type[BaseModel],
        store_name: str | None,
        use_schema: bool,
    ):
        last_exc: Exception | None = None
        for attempt in range(3):
            await self._limiter.wait_for_turn()
            try:
                return await anyio.to_thread.run_sync(
                    self._generate_content,
                    model,
                    prompt,
                    response_model,
                    store_name,
                    use_schema,
                )
            except Exception as exc:
                last_exc = exc
                if attempt == 2 or not self._looks_transient_provider_error(exc):
                    raise
                await asyncio.sleep(2 ** attempt * 2)

        raise GeminiServiceError(f"Provider request failed: {last_exc}")

    async def _get_store_name(self) -> str:
        if self._store_name:
            return self._store_name

        configured = self.settings.gemini_file_search_store
        if configured.startswith("fileSearchStores/"):
            self._store_name = configured
            return configured

        def find_store() -> str:
            for store in self.client.file_search_stores.list():
                if getattr(store, "display_name", None) == configured:
                    return store.name
            raise GeminiServiceError(
                f"Gemini File Search store '{configured}' was not found. "
                "Run backend/manage_data.py upload-all or set GEMINI_FILE_SEARCH_STORE "
                "to a fileSearchStores/... resource name."
            )

        self._store_name = await anyio.to_thread.run_sync(find_store)
        return self._store_name

    def _parse_response(self, response: Any, response_model: type[T]) -> T:
        parsed = getattr(response, "parsed", None)
        if parsed is not None:
            if isinstance(parsed, response_model):
                return parsed
            return response_model.model_validate(parsed)

        text = getattr(response, "text", None)
        if not text:
            raise GeminiServiceError("Provider returned an empty response.")

        try:
            return response_model.model_validate_json(text)
        except ValidationError:
            return response_model.model_validate(self._loads_json_object(text))

    def _loads_json_object(self, text: str) -> Any:
        stripped = text.strip()
        if stripped.startswith("```"):
            lines = stripped.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            stripped = "\n".join(lines).strip()

        first = stripped.find("{")
        last = stripped.rfind("}")
        if first == -1 or last == -1 or last <= first:
            raise GeminiServiceError("Provider response did not contain a JSON object.")
        return json.loads(stripped[first : last + 1])

    def _to_school_analysis(self, school: SchoolKey, output: BaseModel) -> SchoolAnalysis:
        evidence = [
            Evidence.model_validate(item.model_dump() if isinstance(item, BaseModel) else item)
            for item in getattr(output, "primary_evidence", [])
        ]
        reasoning = [
            LegalReasoning.model_validate(
                item.model_dump() if isinstance(item, BaseModel) else item
            )
            for item in getattr(output, "legal_reasoning", [])
        ]
        return SchoolAnalysis(
            school=school,
            school_name=SCHOOL_NAMES[school],
            final_ruling=getattr(output, "final_ruling"),
            primary_evidence=evidence,
            legal_reasoning=reasoning,
            methodology=METHODOLOGIES[school],
        )

    def _looks_like_schema_tool_error(self, exc: Exception) -> bool:
        message = str(exc).lower()
        needles = [
            "response_json_schema",
            "structured",
            "schema",
            "tools",
            "file search",
            "response mime",
        ]
        return any(needle in message for needle in needles)

    def _looks_transient_provider_error(self, exc: Exception) -> bool:
        message = str(exc).lower()
        needles = [
            "429",
            "503",
            "unavailable",
            "resource_exhausted",
            "rate limit",
            "temporarily",
            "try again later",
            "high demand",
        ]
        return any(needle in message for needle in needles)


@lru_cache
def get_gemini_service() -> GeminiService:
    return GeminiService(get_settings())
