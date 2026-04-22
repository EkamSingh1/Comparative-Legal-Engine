from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = BACKEND_DIR.parent


def load_environment() -> None:
    load_dotenv(ROOT_DIR / ".env")
    load_dotenv(BACKEND_DIR / ".env")


def _csv(value: str | None, default: list[str]) -> list[str]:
    if not value:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


def _int(value: str | None, default: int) -> int:
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _float(value: str | None, default: float) -> float:
    if not value:
        return default
    try:
        return float(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    app_name: str
    environment: str
    gemini_api_key: str | None
    gemini_file_search_store: str
    gemini_file_search_model: str
    gemini_synthesis_model: str
    gemini_calls_per_minute: int
    gemini_min_seconds_between_calls: float
    allowed_origins: list[str]

    @classmethod
    def from_env(cls) -> "Settings":
        load_environment()
        return cls(
            app_name=os.getenv("APP_NAME", "Comparative Legal Engine"),
            environment=os.getenv("ENVIRONMENT", "development"),
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            gemini_file_search_store=os.getenv(
                "GEMINI_FILE_SEARCH_STORE", "Islamic-Law-Sources"
            ),
            gemini_file_search_model=os.getenv(
                "GEMINI_FILE_SEARCH_MODEL", "gemini-3.1-flash-lite-preview"
            ),
            gemini_synthesis_model=os.getenv(
                "GEMINI_SYNTHESIS_MODEL", "gemini-3.1-flash-lite-preview"
            ),
            gemini_calls_per_minute=_int(os.getenv("GEMINI_CALLS_PER_MINUTE"), 12),
            gemini_min_seconds_between_calls=_float(
                os.getenv("GEMINI_MIN_SECONDS_BETWEEN_CALLS"), 4.2
            ),
            allowed_origins=_csv(
                os.getenv("ALLOWED_ORIGINS"),
                ["http://localhost:3000", "http://127.0.0.1:3000"],
            ),
        )


@lru_cache
def get_settings() -> Settings:
    return Settings.from_env()
