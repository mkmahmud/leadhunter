from app.scrapers.provider_search import ProviderSearchScraper


class RedditScraper(ProviderSearchScraper):
    def __init__(self) -> None:
        super().__init__("reddit")
