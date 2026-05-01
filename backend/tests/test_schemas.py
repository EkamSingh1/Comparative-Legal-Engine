from schemas import AnalyzeRequest, Evidence, LegalReasoning, MalikiOutput, ShafiiOutput


def test_scenario_normalization() -> None:
    request = AnalyzeRequest(scenario="  A person enters a sale contract online and later disputes the terms.  ")
    assert request.scenario == "A person enters a sale contract online and later disputes the terms."


def test_unified_evidence_shape() -> None:
    evidence = Evidence(
        source_type="Quran",
        citation="Quran, 2:282",
        quote="O believers...",
        relevance="Shows the documentary principle at issue.",
    )
    assert evidence.source_type == "Quran"


def test_reasoning_shape() -> None:
    reasoning = LegalReasoning(
        reasoning_type="Qiyas",
        explanation="The scenario is analogized to a documented transaction.",
    )
    assert reasoning.reasoning_type == "Qiyas"


def test_maliki_filters_non_qiyas_reasoning() -> None:
    output = MalikiOutput(
        final_ruling="The ruling follows established Medinan practice.",
        primary_evidence=[],
        legal_reasoning=[
            {
                "reasoning_type": "Medinan Practice (Amal)",
                "explanation": "Amal belongs in evidence or final ruling, not rational reasoning.",
            },
            {
                "reasoning_type": "Analogical reasoning",
                "explanation": "A narrow analogy remains aligned with Medinan practice.",
            },
        ],
    )

    assert len(output.legal_reasoning) == 1
    assert output.legal_reasoning[0].reasoning_type == "Qiyas"


def test_shafii_filters_textual_adherence_reasoning() -> None:
    output = ShafiiOutput(
        final_ruling="The ruling follows the direct textual evidence.",
        primary_evidence=[],
        legal_reasoning=[
            {
                "reasoning_type": "Textual adherence (Nass)",
                "explanation": "Textual adherence belongs in evidence or final ruling.",
            }
        ],
    )

    assert output.legal_reasoning == []
