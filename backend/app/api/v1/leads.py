from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_session
from app.repositories.leads import LeadRepository
from app.schemas.auth import TokenPayload
from app.schemas.leads import LeadFilters, LeadIngestRequest, LeadIngestResponse, LeadListResponse, LeadRead
from app.services.ai import AILeadAnalyzer
from app.services.enrichment import LeadEnrichmentService
from app.services.scoring import categorize, score_lead


router = APIRouter()


@router.get("", response_model=LeadListResponse)
async def list_leads(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    minimum_lead_score: int = Query(default=0, ge=0, le=100),
    must_have_company_domain: bool = False,
    must_have_email: bool = False,
    session: AsyncSession = Depends(get_session),
    _: TokenPayload = Depends(get_current_user),
) -> LeadListResponse:
    filters = LeadFilters(
        minimum_lead_score=minimum_lead_score,
        must_have_company_domain=must_have_company_domain,
        must_have_email=must_have_email,
    )
    items, total = await LeadRepository(session).list(filters, page, page_size)
    return LeadListResponse(items=[LeadRead.model_validate(item) for item in items], total=total, page=page, page_size=page_size)


@router.post("/ingest", response_model=LeadIngestResponse)
async def ingest_visible_page_leads(
    payload: LeadIngestRequest,
    minimum_lead_score: int = Query(default=0, ge=0, le=100),
    session: AsyncSession = Depends(get_session),
    _: TokenPayload = Depends(get_current_user),
) -> LeadIngestResponse:
    repository = LeadRepository(session)
    analyzer = AILeadAnalyzer()
    enrichment = LeadEnrichmentService()
    saved: list[LeadRead] = []
    skipped = 0
    for raw in payload.items:
        if len(raw.post_content.strip()) < 30:
            skipped += 1
            continue
        enriched = await enrichment.enrich(raw)
        assessment = await analyzer.assess(enriched)
        score = score_lead(enriched, assessment)
        if score < minimum_lead_score:
            skipped += 1
            continue
        lead = await repository.upsert(
            enriched,
            assessment.intent_summary,
            score,
            categorize(score),
            assessment.decision_maker_role,
        )
        await session.flush()
        saved.append(LeadRead.model_validate(lead))
    await session.commit()
    return LeadIngestResponse(items=saved, ingested=len(saved), skipped=skipped)
