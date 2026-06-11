import csv
import io

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_session
from app.repositories.leads import LeadRepository
from app.schemas.auth import TokenPayload
from app.schemas.leads import LeadFilters, LeadRead


router = APIRouter()
CSV_FIELDS = [
    "name",
    "role",
    "company",
    "website",
    "linkedin",
    "email",
    "phone",
    "industry",
    "location",
    "platform",
    "post_url",
    "post_date",
    "intent_summary",
    "lead_score",
]


@router.get("/csv")
async def export_csv(session: AsyncSession = Depends(get_session), _: TokenPayload = Depends(get_current_user)) -> StreamingResponse:
    items, _ = await LeadRepository(session).list(LeadFilters(), 1, 10_000)
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=CSV_FIELDS)
    writer.writeheader()
    for item in items:
        lead = LeadRead.model_validate(item).model_dump()
        writer.writerow({field: lead.get(field, "") for field in CSV_FIELDS})
    buffer.seek(0)
    return StreamingResponse(iter([buffer.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=leads.csv"})


@router.get("/json")
async def export_json(session: AsyncSession = Depends(get_session), _: TokenPayload = Depends(get_current_user)) -> JSONResponse:
    items, _ = await LeadRepository(session).list(LeadFilters(), 1, 10_000)
    return JSONResponse([LeadRead.model_validate(item).model_dump(mode="json") for item in items])
