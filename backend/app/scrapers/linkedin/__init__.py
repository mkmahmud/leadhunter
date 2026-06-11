from app.scrapers.provider_search import ProviderSearchScraper


class LinkedInScraper(ProviderSearchScraper):
    def __init__(self) -> None:
        super().__init__("linkedin")
