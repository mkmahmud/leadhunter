from app.schemas.leads import Platform
from app.scrapers.base import PlatformScraper
from app.scrapers.blogs import CompanyBlogsScraper, PublicBlogsScraper
from app.scrapers.facebook import FacebookScraper
from app.scrapers.github import GitHubScraper
from app.scrapers.hackernews import HackerNewsScraper
from app.scrapers.indiehackers import IndieHackersScraper
from app.scrapers.linkedin import LinkedInScraper
from app.scrapers.medium import MediumScraper
from app.scrapers.producthunt import ProductHuntScraper
from app.scrapers.reddit import RedditScraper
from app.scrapers.stackoverflow import StackOverflowScraper
from app.scrapers.startup_communities import StartupCommunitiesScraper
from app.scrapers.twitter import TwitterScraper
from app.scrapers.youtube import YouTubeScraper


SCRAPERS: dict[Platform, PlatformScraper] = {
    Platform.reddit: RedditScraper(),
    Platform.linkedin: LinkedInScraper(),
    Platform.twitter: TwitterScraper(),
    Platform.indiehackers: IndieHackersScraper(),
    Platform.producthunt: ProductHuntScraper(),
    Platform.medium: MediumScraper(),
    Platform.github: GitHubScraper(),
    Platform.stackoverflow: StackOverflowScraper(),
    Platform.youtube: YouTubeScraper(),
    Platform.facebook: FacebookScraper(),
    Platform.startup_communities: StartupCommunitiesScraper(),
    Platform.hackernews: HackerNewsScraper(),
    Platform.public_blogs: PublicBlogsScraper(),
    Platform.company_blogs: CompanyBlogsScraper(),
}
