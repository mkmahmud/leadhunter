import hashlib
import re
from collections.abc import Sequence

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Lead
from app.schemas.leads import LeadFilters, RawLead


def normalize_key_part(value: str) -> str:
    lowered = value.lower().strip()
    return re.sub(r"[^a-z0-9]+", "", lowered)


def make_dedupe_key(name: str, company: str, website: str) -> str:
    source = "".join(normalize_key_part(part) for part in (name, company, website))
    return hashlib.sha1(source.encode("utf-8")).hexdigest()


class LeadRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert(self, raw: RawLead, intent_summary: str, score: int, category: str, role: str) -> Lead:
        dedupe_key = make_dedupe_key(raw.name, raw.company, raw.website or raw.post_url)
        existing = await self.session.scalar(select(Lead).where(Lead.dedupe_key == dedupe_key))
        if existing:
            existing.lead_score = max(existing.lead_score, score)
            existing.intent_summary = intent_summary or existing.intent_summary
            existing.category = category
            return existing
        lead = Lead(
            dedupe_key=dedupe_key,
            name=raw.name,
            role=role or raw.role,
            company=raw.company,
            website=raw.website,
            linkedin=raw.linkedin,
            email=raw.email,
            phone=raw.phone,
            industry=raw.industry,
            location=raw.location,
            platform=raw.platform,
            post_url=raw.post_url,
            post_content=raw.post_content,
            post_date=raw.post_date,
            intent_summary=intent_summary,
            lead_score=score,
            category=category,
        )
        self.session.add(lead)
        return lead

    async def list(self, filters: LeadFilters, page: int, page_size: int) -> tuple[Sequence[Lead], int]:
        stmt: Select[tuple[Lead]] = select(Lead)
        if filters.must_have_company_domain:
            stmt = stmt.where(Lead.website != "")
        if filters.must_have_email:
            stmt = stmt.where(Lead.email != "")
        if filters.minimum_lead_score:
            stmt = stmt.where(Lead.lead_score >= filters.minimum_lead_score)
        if filters.industry:
            stmt = stmt.where(Lead.industry.ilike(f"%{filters.industry}%"))
        if filters.country:
            stmt = stmt.where(Lead.location.ilike(f"%{filters.country}%"))
        role_filters = []
        if filters.only_founders:
            role_filters.append(Lead.role.in_(["Founder", "Co-Founder"]))
        if filters.only_ceos:
            role_filters.append(Lead.role == "CEO")
        if filters.only_ctos:
            role_filters.append(Lead.role == "CTO")
        if filters.only_decision_makers:
            role_filters.append(Lead.role.in_(["Founder", "Co-Founder", "CEO", "CTO", "Owner", "Director", "VP"]))
        for role_filter in role_filters:
            stmt = stmt.where(role_filter)
        count = await self.session.scalar(select(func.count()).select_from(stmt.subquery()))
        rows = await self.session.scalars(
            stmt.order_by(Lead.lead_score.desc(), Lead.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        )
        return rows.all(), count or 0
