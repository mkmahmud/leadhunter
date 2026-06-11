from app.scrapers.provider_search import ProviderSearchScraper


class StackOverflowScraper(ProviderSearchScraper):
    def __init__(self) -> None:
        super().__init__("stackoverflow")
