from app.scrapers.provider_search import ProviderSearchScraper


class HackerNewsScraper(ProviderSearchScraper):
    def __init__(self) -> None:
        super().__init__("hackernews")
