import re

from app.schemas.leads import RawLead


EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
DOMAIN_RE = re.compile(r"https?://(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})")


class LeadEnrichmentService:
    async def enrich(self, lead: RawLead) -> RawLead:
        text = lead.post_content
        if not lead.email:
            match = EMAIL_RE.search(text)
            if match:
                lead.email = match.group(0)
        if not lead.website:
            match = DOMAIN_RE.search(text)
            if match:
                lead.website = f"https://{match.group(1)}"
        return lead
