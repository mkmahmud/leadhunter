from app.scrapers.provider_search import ProviderSearchScraper


class FacebookScraper(ProviderSearchScraper):
    def __init__(self) -> None:
        super().__init__("facebook")
