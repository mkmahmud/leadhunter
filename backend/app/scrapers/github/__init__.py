from app.scrapers.provider_search import ProviderSearchScraper


class GitHubScraper(ProviderSearchScraper):
    def __init__(self) -> None:
        super().__init__("github")
