from datetime import datetime

import httpx

from app.core.config import settings
from app.schemas.leads import RawLead, SearchRequest
from app.scrapers.base import PlatformScraper
from app.services.date_ranges import resolve_date_range


class GitHubScraper(PlatformScraper):
    platform = "github"

    async def search(self, query: str, request: SearchRequest) -> list[RawLead]:
        start, end = resolve_date_range(request.date_range)
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if settings.github_token:
            headers["Authorization"] = f"Bearer {settings.github_token}"
        async with httpx.AsyncClient(timeout=20, headers=headers) as client:
            response = await client.get(
                "https://api.github.com/search/issues",
                params={
                    "q": f"{query} in:title,body type:issue created:{start.date().isoformat()}..{end.date().isoformat()}",
                    "sort": "created",
                    "order": "desc",
                    "per_page": min(settings.max_results_per_query, 30),
                },
            )
            response.raise_for_status()
        leads: list[RawLead] = []
        for item in response.json().get("items", []):
            user = item.get("user") or {}
            created_at = item.get("created_at")
            leads.append(
                RawLead(
                    name=user.get("login", ""),
                    platform=self.platform,
                    post_url=item.get("html_url", ""),
                    post_content=f"{item.get('title', '')}\n\n{item.get('body') or ''}".strip(),
                    post_date=datetime.fromisoformat(created_at.replace("Z", "+00:00")) if created_at else None,
                )
            )
        return leads
