from abc import ABC, abstractmethod

from app.schemas.leads import RawLead, SearchRequest


class PlatformScraper(ABC):
    platform: str

    @abstractmethod
    async def search(self, query: str, request: SearchRequest) -> list[RawLead]:
        """Return normalized public leads using approved APIs or indexed public data."""
