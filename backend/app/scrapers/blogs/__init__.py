from app.scrapers.provider_search import ProviderSearchScraper


class PublicBlogsScraper(ProviderSearchScraper):
    def __init__(self) -> None:
        super().__init__("public_blogs")


class CompanyBlogsScraper(ProviderSearchScraper):
    def __init__(self) -> None:
        super().__init__("company_blogs")
