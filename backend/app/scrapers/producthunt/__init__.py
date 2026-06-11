from app.scrapers.provider_search import ProviderSearchScraper


class ProductHuntScraper(ProviderSearchScraper):
    def __init__(self) -> None:
        super().__init__("producthunt")
