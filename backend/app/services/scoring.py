from app.schemas.leads import AILeadAssessment, RawLead


ROLE_SCORES = {
    "Founder": 25,
    "Co-Founder": 25,
    "CEO": 25,
    "CTO": 20,
    "Owner": 20,
    "Director": 15,
    "VP": 15,
}


def score_lead(raw: RawLead, assessment: AILeadAssessment) -> int:
    score = ROLE_SCORES.get(assessment.decision_maker_role, 0)
    if raw.website:
        score += 20
    if raw.email:
        score += 10
    if raw.phone:
        score += 10
    if assessment.explicit_hiring_signal or assessment.buying_signal == "High Intent":
        score += 30
    if assessment.mentioned_budget:
        score += 15
    if assessment.mentioned_urgency:
        score += 15
    if assessment.mentioned_timeline:
        score += 10
    return min(score, 100)


def categorize(score: int) -> str:
    if score >= 80:
        return "Hot"
    if score >= 50:
        return "Warm"
    return "Cold"
