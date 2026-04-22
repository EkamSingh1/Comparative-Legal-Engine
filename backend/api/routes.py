from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from core.config import get_settings
from core.prompts import METHODOLOGIES, SCHOOL_NAMES
from schemas import (
    AnalyzeRequest,
    AnalysisResponse,
    HealthResponse,
    SchoolMetadata,
    SchoolKey,
    SchoolsResponse,
)
from services.gemini_service import GeminiServiceError, get_gemini_service


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        gemini_api_key_configured=bool(settings.gemini_api_key),
        file_search_store=settings.gemini_file_search_store,
        file_search_model=settings.gemini_file_search_model,
        synthesis_model=settings.gemini_synthesis_model,
    )


@router.get("/schools", response_model=SchoolsResponse)
def schools() -> SchoolsResponse:
    return SchoolsResponse(
        schools=[
            SchoolMetadata(
                school=school,
                school_name=SCHOOL_NAMES[school],
                methodology=METHODOLOGIES[school],
            )
            for school in SchoolKey
        ]
    )


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(payload: AnalyzeRequest) -> AnalysisResponse:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GEMINI_API_KEY is not configured on the backend.",
        )

    try:
        return await get_gemini_service().analyze(payload.scenario)
    except GeminiServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
