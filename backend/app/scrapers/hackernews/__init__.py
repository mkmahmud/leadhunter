from datetime import UTC, datetime

import httpx

from app.core.config import settings
from app.schemas.leads import RawLead, SearchRequest
from app.scrapers.base import PlatformScraper
from app.services.date_ranges import resolve_date_range


class HackerNewsScraper(PlatformScraper):
    platform = "hackernews"

    async def search(self, query: str, request: SearchRequest) -> list[RawLead]:
        start, end = resolve_date_range(request.date_range)
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                "https://hn.algolia.com/api/v1/search_by_date",
                params={
                    "query": query,
                    "hitsPerPage": settings.max_results_per_query,
                    "numericFilters": f"created_at_i>={int(start.timestamp())},created_at_i<={int(end.timestamp())}",
                },
            )
            response.raise_for_status()
        leads: list[RawLead] = []
        for hit in response.json().get("hits", []):
            object_id = hit.get("objectID", "")
            title = hit.get("title") or hit.get("story_title") or ""
            text = hit.get("comment_text") or hit.get("story_text") or ""
            url = hit.get("url") or hit.get("story_url") or f"https://news.ycombinator.com/item?id={object_id}"
            created_at = hit.get("created_at_i")
            leads.append(
                RawLead(
                    name=hit.get("author", ""),
                    platform=self.platform,
                    post_url=url,
                    post_content=f"{title}\n\n{text}".strip(),
                    post_date=datetime.fromtimestamp(created_at, UTC) if created_at else None,
                )
            )
        return leads
