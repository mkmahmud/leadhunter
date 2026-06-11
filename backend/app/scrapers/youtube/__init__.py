from app.scrapers.provider_search import ProviderSearchScraper


class YouTubeScraper(ProviderSearchScraper):
    def __init__(self) -> None:
        super().__init__("youtube")
