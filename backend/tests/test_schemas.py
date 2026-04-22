from schemas import AnalyzeRequest, Evidence, LegalReasoning


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
