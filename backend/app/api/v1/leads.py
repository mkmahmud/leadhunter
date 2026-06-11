from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_session
from app.repositories.leads import LeadRepository
from app.schemas.auth import TokenPayload
from app.schemas.leads import LeadFilters, LeadListResponse, LeadRead


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
