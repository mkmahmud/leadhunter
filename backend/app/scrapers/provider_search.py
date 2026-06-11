from datetime import UTC, datetime

from app.core.config import settings
from app.schemas.leads import RawLead, SearchRequest
from app.scrapers.base import PlatformScraper


class ProviderSearchScraper(PlatformScraper):
    def __init__(self, platform: str) -> None:
        self.platform = platform

    async def search(self, query: str, request: SearchRequest) -> list[RawLead]:
        if settings.search_provider_api_key:
            return await self._provider_search(query)
        return self._local_fixture(query)

    async def _provider_search(self, query: str) -> list[RawLead]:
        # Wire SerpAPI/Brave/Bing Custom Search here. This route intentionally uses
        # approved search APIs or indexed public pages instead of bypass scraping.
        return []

    def _local_fixture(self, query: str) -> list[RawLead]:
        return [
            RawLead(
                name="Alex Founder",
                role="Founder",
                company="LaunchPilot",
                website="https://launchpilot.example",
                platform=self.platform,
                post_url=f"https://example.com/{self.platform}/lead",
                post_content=f"{query} - Founder looking for a web app developer to build an MVP this month. Budget available.",
                post_date=datetime.now(UTC),
                industry="SaaS",
                location="United States",
            )
        ]
