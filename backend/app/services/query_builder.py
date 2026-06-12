from app.schemas.leads import IntentCategory, Platform, SearchRequest


BASE_INTENTS = [
    "I need a website developer",
    "looking for SaaS developer",
    "need help building MVP",
    "technical help for startup",
    "need web app developer",
    "founder looking for developer",
    "need website redesign",
    "need AI integration",
]

PLATFORM_HINTS: dict[Platform, str] = {
    Platform.reddit: "site:reddit.com",
    Platform.linkedin: "site:linkedin.com/posts OR site:linkedin.com/feed/update",
    Platform.twitter: "site:x.com OR site:twitter.com",
    Platform.indiehackers: "site:indiehackers.com",
    Platform.producthunt: "site:producthunt.com",
    Platform.medium: "site:medium.com",
    Platform.github: "site:github.com/issues OR site:github.com/discussions",
    Platform.stackoverflow: "site:stackoverflow.com/questions",
    Platform.youtube: "site:youtube.com",
    Platform.facebook: "site:facebook.com/pages",
    Platform.startup_communities: "startup founder community",
    Platform.hackernews: "site:news.ycombinator.com",
    Platform.public_blogs: "blog founder need developer",
    Platform.company_blogs: "company blog hiring developer startup",
}


def build_queries(request: SearchRequest, platform: Platform) -> list[str]:
    keywords = request.keywords or BASE_INTENTS
    categories = [category.value for category in request.intent_categories] or [IntentCategory.web_development.value]
    if platform in {Platform.github, Platform.hackernews}:
        return [f'"{keyword}" "{category}" founder OR CEO OR CTO OR owner' for keyword in keywords for category in categories[:3]][:8]
    platform_hint = PLATFORM_HINTS[platform]
    queries: list[str] = []
    for keyword in keywords:
        for category in categories[:4]:
            queries.append(f'{platform_hint} "{keyword}" "{category}" founder OR CEO OR CTO OR owner')
    return queries[:12]
