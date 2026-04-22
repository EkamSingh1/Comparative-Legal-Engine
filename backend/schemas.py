from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator


DISCLAIMER = (
    "Educational demonstration only. This output is not legal advice, not a fatwa, "
    "and not a substitute for a qualified lawyer, scholar, or jurisdiction-specific authority."
)


def normalize_source_label(value: object) -> object:
    if not isinstance(value, str):
        return value
    lowered = value.strip().lower()
    if "qur" in lowered:
        return "Quran"
    if "hadith" in lowered or "sunnah" in lowered:
        return "Hadith"
    if "ijma" in lowered or "consensus" in lowered or "medina" in lowered:
        return "Ijma"
    return value


def normalize_reasoning_label(value: object) -> object:
    if not isinstance(value, str):
        return value
    lowered = value.strip().lower()
    if "istihsan" in lowered or "juristic preference" in lowered:
        return "Istihsan"
    if "qiyas" in lowered or "analog" in lowered:
        return "Qiyas"
    return value


class SchoolKey(str, Enum):
    hanafi = "hanafi"
    maliki = "maliki"
    shafii = "shafii"
    hanbali = "hanbali"


class AnalyzeRequest(BaseModel):
    scenario: str = Field(
        min_length=20,
        max_length=4000,
        description="The user's case scenario to compare across the four Sunni schools.",
    )

    @field_validator("scenario")
    @classmethod
    def normalize_scenario(cls, value: str) -> str:
        normalized = " ".join(value.strip().split())
        if len(normalized) < 20:
            raise ValueError("Please provide a more complete scenario.")
        return normalized


class Evidence(BaseModel):
    source_type: Literal["Quran", "Hadith", "Ijma"] = Field(
        description="The category of textual source used by the school."
    )
    citation: str = Field(description="Document and page, section, book, or verse reference.")
    quote: str = Field(description="Short quote from retrieved context.")
    relevance: str = Field(description="How the quote applies to the scenario.")

    @field_validator("source_type", mode="before")
    @classmethod
    def normalize_source_type(cls, value: object) -> object:
        return normalize_source_label(value)


class LegalReasoning(BaseModel):
    reasoning_type: Literal["Qiyas", "Istihsan"] = Field(
        description="The rational method used, where the school permits it."
    )
    explanation: str = Field(description="Concise explanation of the legal reasoning.")

    @field_validator("reasoning_type", mode="before")
    @classmethod
    def normalize_reasoning_type(cls, value: object) -> object:
        return normalize_reasoning_label(value)


class Methodology(BaseModel):
    authority_order: list[str]
    reasoning_posture: str
    source_scope: list[str]


class SchoolAnalysis(BaseModel):
    school: SchoolKey
    school_name: str
    final_ruling: str
    primary_evidence: list[Evidence]
    legal_reasoning: list[LegalReasoning] = Field(default_factory=list)
    methodology: Methodology


class SynthesisOutput(BaseModel):
    core_divergence: str = Field(
        description="The fundamental methodological difference behind the rulings."
    )
    consensus_point: str = Field(
        description="Any agreement among the schools, or 'No consensus reached'."
    )


class AnalysisResponse(BaseModel):
    scenario: str
    disclaimer: str = DISCLAIMER
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    synthesis: SynthesisOutput
    schools: list[SchoolAnalysis]


class HealthResponse(BaseModel):
    status: Literal["ok"]
    gemini_api_key_configured: bool
    file_search_store: str
    file_search_model: str
    synthesis_model: str


class SchoolMetadata(BaseModel):
    school: SchoolKey
    school_name: str
    methodology: Methodology


class SchoolsResponse(BaseModel):
    schools: list[SchoolMetadata]


class HanafiEvidence(BaseModel):
    source_type: Literal["Quran", "Hadith", "Ijma"] = Field(
        description="The category of the textual source."
    )
    citation: str = Field(
        description="Specific reference, e.g. 'Quran 2:282' or 'A Digest of Moohummudan Law, Page 45'."
    )
    quote: str = Field(description="Exact short quotation extracted from File Search context.")
    relevance: str = Field(description="How this quote applies to the user's case.")

    @field_validator("source_type", mode="before")
    @classmethod
    def normalize_source_type(cls, value: object) -> object:
        return normalize_source_label(value)


class HanafiReasoning(BaseModel):
    reasoning_type: Literal["Qiyas", "Istihsan"] = Field(
        description="The specific type of Hanafi rational deduction applied."
    )
    explanation: str = Field(
        description="If Qiyas, explain the analogy. If Istihsan, explain why equity, practicality, or public interest overrides strict analogy."
    )

    @field_validator("reasoning_type", mode="before")
    @classmethod
    def normalize_reasoning_type(cls, value: object) -> object:
        return normalize_reasoning_label(value)


class HanafiOutput(BaseModel):
    final_ruling: str = Field(description="Concise Hanafi ruling in 2 to 3 sentences.")
    primary_evidence: list[HanafiEvidence]
    legal_reasoning: list[HanafiReasoning]


class MalikiEvidence(BaseModel):
    source_type: Literal["Quran", "Ijma"] = Field(
        description="The category of the textual source."
    )
    citation: str = Field(
        description="Specific reference, e.g. 'Al-Muwatta of Imam Malik, Book 2, Page 45'."
    )
    quote: str = Field(description="Exact short quotation extracted from File Search context.")
    relevance: str = Field(description="How this quote applies to the user's case.")

    @field_validator("source_type", mode="before")
    @classmethod
    def normalize_source_type(cls, value: object) -> object:
        return normalize_source_label(value)


class MalikiReasoning(BaseModel):
    reasoning_type: Literal["Qiyas"] = Field(description="Maliki analogical reasoning.")
    explanation: str = Field(
        description="Explain the analogy and how it aligns with Medinan tradition."
    )

    @field_validator("reasoning_type", mode="before")
    @classmethod
    def normalize_reasoning_type(cls, value: object) -> object:
        return normalize_reasoning_label(value)


class MalikiOutput(BaseModel):
    final_ruling: str = Field(description="Concise Maliki ruling in 2 to 3 sentences.")
    primary_evidence: list[MalikiEvidence]
    legal_reasoning: list[MalikiReasoning]


class ShafiiEvidence(BaseModel):
    source_type: Literal["Quran", "Hadith"] = Field(
        description="The category of the textual source."
    )
    citation: str = Field(description="Specific reference, e.g. 'Sahih Bukhari, Page 45'.")
    quote: str = Field(description="Exact short quotation extracted from File Search context.")
    relevance: str = Field(description="How this quote applies to the user's case.")

    @field_validator("source_type", mode="before")
    @classmethod
    def normalize_source_type(cls, value: object) -> object:
        return normalize_source_label(value)


class ShafiiReasoning(BaseModel):
    reasoning_type: Literal["Qiyas"] = Field(description="Strict Shafi'i analogical reasoning.")
    explanation: str = Field(
        description="Explain the narrow analogy and state that textual certainty was prioritized over preference."
    )

    @field_validator("reasoning_type", mode="before")
    @classmethod
    def normalize_reasoning_type(cls, value: object) -> object:
        return normalize_reasoning_label(value)


class ShafiiOutput(BaseModel):
    final_ruling: str = Field(description="Concise Shafi'i ruling in 2 to 3 sentences.")
    primary_evidence: list[ShafiiEvidence]
    legal_reasoning: list[ShafiiReasoning]


class HanbaliEvidence(BaseModel):
    source_type: Literal["Quran", "Hadith", "Ijma"] = Field(
        description="The category of the textual source."
    )
    citation: str = Field(
        description="Specific reference, e.g. 'Musnad Ahmad Bin Hanbal, Page 45'."
    )
    quote: str = Field(description="Exact short quotation extracted from File Search context.")
    relevance: str = Field(description="How this quote applies to the user's case.")

    @field_validator("source_type", mode="before")
    @classmethod
    def normalize_source_type(cls, value: object) -> object:
        return normalize_source_label(value)


class HanbaliOutput(BaseModel):
    final_ruling: str = Field(
        description="Concise Hanbali ruling in 2 to 3 sentences, noting textual adherence over analogy."
    )
    primary_evidence: list[HanbaliEvidence]


SCHOOL_OUTPUT_MODELS = {
    SchoolKey.hanafi: HanafiOutput,
    SchoolKey.maliki: MalikiOutput,
    SchoolKey.shafii: ShafiiOutput,
    SchoolKey.hanbali: HanbaliOutput,
}
