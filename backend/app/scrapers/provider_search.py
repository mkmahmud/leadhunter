from datetime import UTC, datetime
from urllib.parse import urlparse

import httpx

from app.core.config import settings
from app.schemas.leads import RawLead, SearchRequest
from app.scrapers.base import PlatformScraper
from app.scrapers.errors import ScraperConfigurationError
from app.services.date_ranges import resolve_date_range


class ProviderSearchScraper(PlatformScraper):
    def __init__(self, platform: str) -> None:
        self.platform = platform

    async def search(self, query: str, request: SearchRequest) -> list[RawLead]:
        if not settings.active_search_api_key:
            raise ScraperConfigurationError(
                f"{self.platform} needs a web search provider key. Set BRAVE_SEARCH_API_KEY or SERPAPI_API_KEY in backend/.env."
            )
        return await self._provider_search(query, request)

    async def _provider_search(self, query: str, request: SearchRequest) -> list[RawLead]:
        if settings.search_provider == "serpapi":
            return await self._serpapi_search(query, request)
        return await self._brave_search(query, request)

    async def _brave_search(self, query: str, request: SearchRequest) -> list[RawLead]:
        assert settings.active_search_api_key
        params = {"q": query, "count": settings.max_results_per_query, "safesearch": "moderate"}
        freshness = self._brave_freshness(request)
        if freshness:
            params["freshness"] = freshness
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                "https://api.search.brave.com/res/v1/web/search",
                params=params,
                headers={
                    "Accept": "application/json",
                    "X-Subscription-Token": settings.active_search_api_key,
                },
            )
            response.raise_for_status()
        results = response.json().get("web", {}).get("results", [])
        return [self._from_search_result(item.get("title", ""), item.get("description", ""), item.get("url", "")) for item in results]

    async def _serpapi_search(self, query: str, request: SearchRequest) -> list[RawLead]:
        assert settings.active_search_api_key
        params = {
            "engine": "google",
            "q": query,
            "api_key": settings.active_search_api_key,
            "num": settings.max_results_per_query,
        }
        tbs = self._serpapi_tbs(request)
        if tbs:
            params["tbs"] = tbs
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                "https://serpapi.com/search.json",
                params=params,
            )
            response.raise_for_status()
        results = response.json().get("organic_results", [])
        return [self._from_search_result(item.get("title", ""), item.get("snippet", ""), item.get("link", "")) for item in results]

    def _from_search_result(self, title: str, description: str, url: str) -> RawLead:
        parsed = urlparse(url)
        domain = parsed.netloc.removeprefix("www.")
        return RawLead(
            name="",
            company=domain,
            website=f"{parsed.scheme}://{parsed.netloc}" if parsed.scheme and parsed.netloc else "",
            platform=self.platform,
            post_url=url,
            post_content=f"{title}\n\n{description}".strip(),
            post_date=datetime.now(UTC),
        )

    def _brave_freshness(self, request: SearchRequest) -> str | None:
        if request.date_range.preset in {"today", "last_24_hours"}:
            return "pd"
        if request.date_range.preset in {"last_3_days", "last_7_days"}:
            return "pw"
        if request.date_range.preset == "last_30_days":
            return "pm"
        return None

    def _serpapi_tbs(self, request: SearchRequest) -> str | None:
        if request.date_range.preset in {"today", "last_24_hours"}:
            return "qdr:d"
        if request.date_range.preset == "last_3_days":
            return "qdr:d3"
        if request.date_range.preset == "last_7_days":
            return "qdr:w"
        if request.date_range.preset == "last_30_days":
            return "qdr:m"
        start, end = resolve_date_range(request.date_range)
        return f"cdr:1,cd_min:{start:%m/%d/%Y},cd_max:{end:%m/%d/%Y}"
