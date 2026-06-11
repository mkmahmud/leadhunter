from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import JobStatus, Search, SearchJob
from app.schemas.leads import SearchRequest


class SearchJobRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, request: SearchRequest) -> SearchJob:
        job = SearchJob(filters=request.model_dump(mode="json"), status=JobStatus.queued)
        self.session.add(job)
        await self.session.flush()
        return job

    async def get(self, job_id: str) -> SearchJob | None:
        return await self.session.scalar(select(SearchJob).where(SearchJob.id == job_id))

    async def mark_running(self, job: SearchJob) -> None:
        job.status = JobStatus.running
        job.started_at = datetime.now(UTC)

    async def mark_completed(self, job: SearchJob) -> None:
        job.status = JobStatus.completed
        job.completed_at = datetime.now(UTC)

    async def mark_failed(self, job: SearchJob, error: str) -> None:
        job.status = JobStatus.failed
        job.completed_at = datetime.now(UTC)
        job.error = error

    def add_search(self, job: SearchJob, platform: str, query: str, results_count: int) -> None:
        self.session.add(Search(job_id=job.id, platform=platform, query=query, results_count=results_count))
