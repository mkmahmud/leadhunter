import asyncio

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db import session as db_session
from app.repositories.search_jobs import SearchJobRepository
from app.schemas.auth import TokenPayload
from app.schemas.leads import SearchJobResponse, SearchRequest, SearchStatusResponse
from app.services.events import broker
from app.services.search import SearchService


router = APIRouter()


async def run_search_job(job_id: str, request: SearchRequest) -> None:
    async with db_session.AsyncSessionLocal() as session:
        await SearchService(session).run(job_id, request)


@router.post("", response_model=SearchJobResponse)
async def start_search(
    request: SearchRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(db_session.get_session),
    _: TokenPayload = Depends(get_current_user),
) -> SearchJobResponse:
    repo = SearchJobRepository(session)
    job = await repo.create(request)
    await session.commit()
    background_tasks.add_task(run_search_job, job.id, request)
    return SearchJobResponse(job_id=job.id, status=job.status.value)


@router.get("/{job_id}", response_model=SearchStatusResponse)
async def status(job_id: str, session: AsyncSession = Depends(db_session.get_session), _: TokenPayload = Depends(get_current_user)) -> SearchStatusResponse:
    job = await SearchJobRepository(session).get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return SearchStatusResponse(
        job_id=job.id,
        status=job.status.value,
        started_at=job.started_at,
        completed_at=job.completed_at,
        error=job.error,
    )


@router.get("/{job_id}/events")
async def events(job_id: str) -> StreamingResponse:
    async def stream():
        async for message in broker.subscribe(f"job:{job_id}"):
            yield f"data: {message}\n\n"
            await asyncio.sleep(0)

    return StreamingResponse(stream(), media_type="text/event-stream")
