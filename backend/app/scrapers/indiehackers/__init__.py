from app.scrapers.provider_search import ProviderSearchScraper


class IndieHackersScraper(ProviderSearchScraper):
    def __init__(self) -> None:
        super().__init__("indiehackers")
