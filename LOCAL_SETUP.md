# Local Setup

This project no longer returns dummy leads. It has two modes:

- Free current-page capture: open a public page yourself, then click `Capture Page` in the extension side panel. No paid search API key is required.
- API search: run backend searches across platforms. This requires Brave Search or SerpAPI for broad web discovery.

The free mode only extracts visible/public DOM content from the current tab. It does not bypass login walls, rate limits, robots controls, captchas, private APIs, or hidden access controls.

## Key Requirements

Mandatory for free current-page capture:

- No platform API key required.
- Backend must be running locally.
- Chrome extension must be loaded from `extension/dist`.

Mandatory for broad API platform search:

- `BRAVE_SEARCH_API_KEY` if `SEARCH_PROVIDER=brave`
- or `SERPAPI_API_KEY` if `SEARCH_PROVIDER=serpapi`

At least one of those is required for:

- Reddit
- LinkedIn
- X/Twitter
- Indie Hackers
- Product Hunt
- Medium
- Stack Overflow
- YouTube
- Facebook Pages
- Startup Communities
- Public Blogs
- Company Blogs

Not mandatory:

- `OPENAI_API_KEY`: optional. Without it, the backend uses local heuristic intent detection and scoring. Use OpenAI for better extraction.
- `GITHUB_TOKEN`: optional. GitHub search works without it, but unauthenticated rate limits are low. Add a fine-grained token for reliable local testing.
- `REDIS_URL`: optional for the current local FastAPI background-task flow. Required if you move jobs fully to Celery workers.
- `DATABASE_URL`: optional locally. If omitted, backend uses SQLite at `backend/leadhunter.db`.

No key required:

- Hacker News uses the public Algolia HN search API.

## Recommended Local Path

Use this if you want the simplest free setup with real data from pages you open:

1. Create `backend/.env`.

```env
APP_ENV=local
DATABASE_URL=sqlite+aiosqlite:///./leadhunter.db
JWT_SECRET=replace-with-a-long-random-secret
CSRF_TOKEN=local-csrf-token
CORS_ORIGINS=http://localhost:5173
OPENAI_API_KEY=your_openai_key_optional_but_recommended
MAX_RESULTS_PER_QUERY=10
```

For paid/broad backend API search, add one of these:

```env
SEARCH_PROVIDER=brave
BRAVE_SEARCH_API_KEY=your_brave_search_key
```

or:

```env
SEARCH_PROVIDER=serpapi
SERPAPI_API_KEY=your_serpapi_key
```

2. Install and run the backend.

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

3. In a second terminal, build the extension.

```bash
cd extension
npm install
npm run build
```

4. Load the Chrome extension.

- Open `chrome://extensions`
- Enable Developer Mode
- Click `Load unpacked`
- Select `P:\Codexmine\leadhunter\extension\dist`
- Click the extension icon. The side panel opens.

5. Free first test.

- Open a normal webpage with visible posts, for example Hacker News search, Reddit search results, GitHub issues, LinkedIn feed, X search, Indie Hackers posts, or a public blog comments page.
- Open the extension side panel.
- Click `Capture Page`.
- Leads are extracted from the visible page, sent to your local backend, scored, deduped, and saved.

6. Optional API search test.

For no-key testing, select only:

- GitHub
- Hacker News

For full platform testing, add your Brave or SerpAPI key, then select the other platforms.

## Common Local Problems

`Configuration error: <platform> needs a web search provider key`

You selected a platform that needs Brave or SerpAPI. Add `BRAVE_SEARCH_API_KEY` or `SERPAPI_API_KEY` to `backend/.env`, restart `uvicorn`, and search again.

No leads appear but no error

- For `Capture Page`, make sure actual posts are visible in the current tab.
- Scroll or search on the platform first, then click `Capture Page`.
- Lower `Minimum Lead Score`.
- Disable `Must Have Email`.
- Disable `Must Have Company Domain`.
- Try fewer platforms first: `Hacker News`, `GitHub`, then broaden.
- Add `OPENAI_API_KEY` for stronger role and intent extraction.

GitHub returns rate-limit errors

Add `GITHUB_TOKEN` to `backend/.env` and restart the backend.
