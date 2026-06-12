import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.leads import LeadRepository
from app.repositories.search_jobs import SearchJobRepository
from app.schemas.leads import LeadRead, SearchRequest
from app.scrapers.errors import ScraperConfigurationError
from app.scrapers.registry import SCRAPERS
from app.services.ai import AILeadAnalyzer
from app.services.enrichment import LeadEnrichmentService
from app.services.events import broker
from app.services.query_builder import build_queries
from app.services.scoring import categorize, score_lead


class SearchService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.jobs = SearchJobRepository(session)
        self.leads = LeadRepository(session)
        self.ai = AILeadAnalyzer()
        self.enrichment = LeadEnrichmentService()

    async def run(self, job_id: str, request: SearchRequest) -> None:
        job = await self.jobs.get(job_id)
        if not job:
            return
        try:
            await self.jobs.mark_running(job)
            await self.session.commit()
            for platform in request.platforms:
                scraper = SCRAPERS[platform]
                for query in build_queries(request, platform):
                    raw_results = await scraper.search(query, request)
                    self.jobs.add_search(job, platform.value, query, len(raw_results))
                    for raw in raw_results:
                        enriched = await self.enrichment.enrich(raw)
                        assessment = await self.ai.assess(enriched)
                        score = score_lead(enriched, assessment)
                        if not self._passes_filters(enriched.website, enriched.email, score, assessment.decision_maker_role, request):
                            continue
                        lead = await self.leads.upsert(
                            enriched,
                            assessment.intent_summary,
                            score,
                            categorize(score),
                            assessment.decision_maker_role,
                        )
                        await self.session.flush()
                        await broker.publish(f"job:{job_id}", {"type": "lead", "lead": LeadRead.model_validate(lead).model_dump(mode="json")})
                    await self.session.commit()
                    await asyncio.sleep(0)
            await self.jobs.mark_completed(job)
            await self.session.commit()
            await broker.publish(f"job:{job_id}", {"type": "completed", "job_id": job_id})
        except Exception as exc:
            message = str(exc)
            if isinstance(exc, ScraperConfigurationError):
                message = f"Configuration error: {message}"
            await self.jobs.mark_failed(job, message)
            await self.session.commit()
            await broker.publish(f"job:{job_id}", {"type": "failed", "error": message})

    def _passes_filters(self, website: str, email: str, score: int, role: str, request: SearchRequest) -> bool:
        filters = request.filters
        if filters.must_have_company_domain and not website:
            return False
        if filters.must_have_email and not email:
            return False
        if score < filters.minimum_lead_score:
            return False
        if filters.only_founders and role not in {"Founder", "Co-Founder"}:
            return False
        if filters.only_ceos and role != "CEO":
            return False
        if filters.only_ctos and role != "CTO":
            return False
        if filters.only_decision_makers and role not in {"Founder", "Co-Founder", "CEO", "CTO", "Owner", "Director", "VP"}:
            return False
        return True
