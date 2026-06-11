from app.schemas.leads import AILeadAssessment, RawLead
from app.services.scoring import categorize, score_lead


def test_hot_founder_with_domain_and_explicit_intent() -> None:
    raw = RawLead(platform="reddit", website="https://example.com", email="founder@example.com")
    assessment = AILeadAssessment(
        decision_maker_role="Founder",
        buying_signal="High Intent",
        need="MVP developer",
        intent_summary="Founder needs MVP developer",
        explicit_hiring_signal=True,
        mentioned_budget=True,
    )

    score = score_lead(raw, assessment)

    assert score == 100
    assert categorize(score) == "Hot"
