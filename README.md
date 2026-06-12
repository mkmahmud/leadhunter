# AI Founder Intent Lead Intelligence Platform

Production-shaped Chrome Extension and FastAPI platform for discovering founders, CEOs, CTOs, owners, and decision makers who publicly express intent for website, SaaS, MVP, AI integration, automation, API integration, and technical co-founder help.

## What Is Included

- Chrome Manifest V3 extension with a React 19 side panel UI.
- Free current-page capture mode that extracts visible public posts from the tab you opened.
- FastAPI backend with typed request/response schemas.
- Per-platform scraper adapter folders for Reddit, LinkedIn, X/Twitter, Indie Hackers, Product Hunt, Medium, GitHub, Stack Overflow, YouTube, Facebook, startup communities, Hacker News, public blogs, and company blogs.
- ToS-safe collection model: approved APIs, official API tokens, or indexed public search provider data only. No dummy data is returned.
- AI intent analysis with OpenAI structured output when `OPENAI_API_KEY` is configured, plus a local heuristic fallback.
- Lead scoring, hot/warm/cold categories, deduplication, enrichment, pagination, CSV export, JSON export, and SSE live job updates.
- Docker Compose for API, worker, Postgres, Redis, and Nginx.

## Local Backend

```bash
cd backend
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Local development uses SQLite by default, so the API starts without a running Postgres instance.

If `.venv` does not exist yet, create it first with `python -m venv .venv`. If that command fails because `.venv` already exists, skip creation and just activate the existing environment. If the environment is corrupted, delete the `.venv` folder and recreate it.

For free local scraping from pages you open, read [LOCAL_SETUP.md](LOCAL_SETUP.md). Broad backend API search still requires `BRAVE_SEARCH_API_KEY` or `SERPAPI_API_KEY`.

## Local Extension

```bash
cd extension
npm install
npm run dev
```

For Chrome loading:

```bash
cd extension
npm run build
```

Then open `chrome://extensions`, enable Developer Mode, and load `extension/dist`.

## Docker

```bash
docker compose up --build
```

API: `http://localhost:8000`

Nginx proxy: `http://localhost:8080`

## Platform Compliance

The scraper architecture intentionally isolates every platform and avoids bypassing access controls. Connect each adapter to approved APIs or search providers:

- Reddit: official Reddit API or approved search provider.
- LinkedIn: approved partner APIs or indexed public pages where permitted.
- X/Twitter: official X API.
- Facebook and YouTube: Meta Graph API and YouTube Data API.
- GitHub: GitHub REST/GraphQL APIs.
- Stack Overflow: Stack Exchange API.
- Blogs, Hacker News, Indie Hackers, Product Hunt: approved APIs, RSS, or public indexed search where permitted.

## API Surface

- `POST /api/search`
- `GET /api/search/{job_id}`
- `GET /api/search/{job_id}/events`
- `GET /api/leads`
- `GET /api/export/csv`
- `GET /api/export/json`

## Next Production Steps

- Replace the local auth shortcut with a real user repository and password verification.
- Add Alembic revision files for managed migrations.
- Add richer native adapters for each platform where official APIs are available.
- Add platform-specific content extractors for more accurate current-page capture.
- Move long-running jobs fully into Celery instead of FastAPI background tasks.
- Add Playwright E2E coverage for the extension and integration tests for search jobs.
