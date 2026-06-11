from app.scrapers.provider_search import ProviderSearchScraper


class TwitterScraper(ProviderSearchScraper):
    def __init__(self) -> None:
        super().__init__("twitter")
