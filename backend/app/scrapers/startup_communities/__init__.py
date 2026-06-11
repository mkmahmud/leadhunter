from app.scrapers.provider_search import ProviderSearchScraper


class StartupCommunitiesScraper(ProviderSearchScraper):
    def __init__(self) -> None:
        super().__init__("startup_communities")
