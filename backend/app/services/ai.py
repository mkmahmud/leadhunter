import re

from app.core.config import settings
from app.schemas.leads import AILeadAssessment, RawLead


class AILeadAnalyzer:
    async def assess(self, lead: RawLead) -> AILeadAssessment:
        if settings.openai_api_key:
            return await self._assess_with_openai(lead)
        return self._assess_heuristically(lead)

    async def _assess_with_openai(self, lead: RawLead) -> AILeadAssessment:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.responses.parse(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": "Extract decision-maker role, buying intent, and concrete technical need from public lead posts.",
                },
                {"role": "user", "content": lead.model_dump_json()},
            ],
            text_format=AILeadAssessment,
        )
        return response.output_parsed

    def _assess_heuristically(self, lead: RawLead) -> AILeadAssessment:
        text = f"{lead.role} {lead.post_content}".lower()
        role = "Unknown"
        for candidate in ["Founder", "Co-Founder", "CEO", "CTO", "Owner", "Director", "VP", "Manager"]:
            if candidate.lower().replace("-", " ") in text or candidate.lower() in text:
                role = candidate
                break
        explicit = bool(re.search(r"\b(need|looking for|hire|seeking|help building|redesign|integrat(e|ion))\b", text))
        budget = bool(re.search(r"\b(\$|budget|paid|rate|quote|proposal)\b", text))
        urgency = bool(re.search(r"\b(urgent|asap|immediately|this week|soon)\b", text))
        timeline = bool(re.search(r"\b(today|tomorrow|week|month|deadline|timeline|launch)\b", text))
        signal = "High Intent" if explicit and (urgency or budget or timeline) else "Medium Intent" if explicit else "Low Intent"
        need = "Technical help"
        for phrase in ["website redesign", "website developer", "saas developer", "mvp developer", "ai integration", "api integration", "workflow automation", "web app developer"]:
            if phrase in text:
                need = phrase.title()
                break
        return AILeadAssessment(
            decision_maker_role=role,
            buying_signal=signal,
            need=need,
            intent_summary=f"{signal}: {need}",
            mentioned_budget=budget,
            mentioned_urgency=urgency,
            mentioned_timeline=timeline,
            explicit_hiring_signal=explicit,
        )
