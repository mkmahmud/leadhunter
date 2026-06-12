from datetime import date, datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class Platform(StrEnum):
    reddit = "reddit"
    linkedin = "linkedin"
    twitter = "twitter"
    indiehackers = "indiehackers"
    producthunt = "producthunt"
    medium = "medium"
    github = "github"
    stackoverflow = "stackoverflow"
    youtube = "youtube"
    facebook = "facebook"
    startup_communities = "startup_communities"
    hackernews = "hackernews"
    public_blogs = "public_blogs"
    company_blogs = "company_blogs"


class IntentCategory(StrEnum):
    website_design = "Website Design"
    web_development = "Web Development"
    saas = "SaaS"
    mvp = "MVP"
    ai_development = "AI Development"
    automation = "Automation"
    technical_cofounder = "Technical Co-Founder"
    api_integration = "API Integration"


class DateRange(BaseModel):
    preset: Literal["today", "last_24_hours", "last_3_days", "last_7_days", "last_30_days", "custom"]
    start_date: date | None = None
    end_date: date | None = None


class LeadFilters(BaseModel):
    only_founders: bool = False
    only_ceos: bool = False
    only_ctos: bool = False
    only_decision_makers: bool = False
    must_have_company_domain: bool = False
    must_have_email: bool = False
    minimum_lead_score: int = Field(default=0, ge=0, le=100)
    country: str | None = None
    industry: str | None = None
    company_size: str | None = None


class SearchRequest(BaseModel):
    platforms: list[Platform] = Field(min_length=1)
    date_range: DateRange
    keywords: list[str] = Field(default_factory=list)
    intent_categories: list[IntentCategory] = Field(default_factory=list)
    filters: LeadFilters = Field(default_factory=LeadFilters)


class SearchJobResponse(BaseModel):
    job_id: str
    status: str


class SearchStatusResponse(BaseModel):
    job_id: str
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    error: str = ""


class LeadRead(BaseModel):
    id: str
    name: str
    role: str
    company: str
    website: str
    linkedin: str
    email: str
    phone: str
    industry: str
    location: str
    platform: str
    post_url: str
    post_content: str = ""
    post_date: datetime | None
    intent_summary: str
    lead_score: int
    category: str
    created_at: datetime

    model_config = {"from_attributes": True}


class LeadListResponse(BaseModel):
    items: list[LeadRead]
    total: int
    page: int
    page_size: int


class RawLead(BaseModel):
    name: str = ""
    role: str = "Unknown"
    company: str = ""
    website: str = ""
    linkedin: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    industry: str = ""
    platform: str
    post_url: str = ""
    post_content: str = ""
    post_date: datetime | None = None


class LeadIngestRequest(BaseModel):
    items: list[RawLead] = Field(default_factory=list, max_length=200)


class LeadIngestResponse(BaseModel):
    items: list[LeadRead]
    ingested: int
    skipped: int


class AILeadAssessment(BaseModel):
    decision_maker_role: Literal["Founder", "Co-Founder", "CEO", "CTO", "Owner", "Director", "VP", "Manager", "Employee", "Unknown"]
    buying_signal: Literal["High Intent", "Medium Intent", "Low Intent", "No Intent"]
    need: str
    intent_summary: str
    mentioned_budget: bool = False
    mentioned_urgency: bool = False
    mentioned_timeline: bool = False
    explicit_hiring_signal: bool = False
