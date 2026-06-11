from app.scrapers.provider_search import ProviderSearchScraper


class MediumScraper(ProviderSearchScraper):
    def __init__(self) -> None:
        super().__init__("medium")
