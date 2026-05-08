# CarGrab

> One site to find the best used car deals — listings aggregated from CarMax, MarketCheck, and more.

CarGrab is a full-stack used car listing aggregator. It polls multiple data sources on a schedule, normalizes all listings into a single database, and serves them through a fast REST API consumed by a dark-mode Next.js frontend. The backend is designed from the start to also power a mobile app.

---

## Screenshots

| Home | Search | Listing Detail |
|------|--------|----------------|
| Hero search + featured deals grid | Filter sidebar + paginated results | Photo gallery, specs, price history |

*(Start the app and visit http://localhost:3000)*

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI 0.115, SQLAlchemy 2 (async), Alembic |
| Database | PostgreSQL 16 |
| Cache / Queue | Redis 7, Celery 5 |
| Data sources | CarMax (unofficial API), MarketCheck (commercial), NHTSA (free VIN decoder) |
| Frontend | Next.js 15, TypeScript, Tailwind CSS v4 |
| UI Style | Dark glassmorphism — navy + cyan accents (inspired by worldwideview.dev) |
| Auth | JWT (python-jose + passlib/bcrypt) |
| Containerization | Docker Compose |

---

## Quick Start

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Node.js 18+](https://nodejs.org/)
- [Anaconda / Miniconda](https://docs.conda.io/en/latest/miniconda.html)

### 1 — Clone & configure

```bash
git clone https://github.com/YOUR_USERNAME/cargrab.git
cd cargrab
cp .env.example .env
```

Edit `.env` if needed (defaults work for local development out of the box).

### 2 — Set up Python environment

```bash
conda create -n car python=3.12
conda activate car
pip install -r backend/requirements.txt
```

### 3 — Start the database and services

```bash
# Start Postgres + Redis + Backend API + Celery worker
docker compose up -d

# Apply database migrations
cd backend && conda run -n car alembic upgrade head
```

### 4 — Start the frontend

```bash
cd frontend
npm install
npm run dev
```

### 5 — Open the app

| URL | Description |
|-----|-------------|
| http://localhost:3000 | Frontend |
| http://localhost:8000/api/docs | Interactive API docs (Swagger UI) |

### 6 — Populate with real listings

**Option A — Seed data (works immediately, no API key needed):**

```bash
docker exec cargrab-backend-1 python seed.py
```

This inserts 30 realistic demo listings (Toyota, Honda, Ford, BMW, Tesla, etc.) directly into the database.

**Option B — Live data via Auto.dev (requires free API key):**

Add your key to `.env`:
```
AUTODEV_API_KEY=your_key_here
```

Then restart and trigger a poll:
```bash
docker compose up -d --force-recreate backend celery
docker exec cargrab-celery-1 celery -A app.tasks.celery_app call app.tasks.ingest.poll_autodev
```

Wait ~2 minutes (5 zip codes × 10 pages). The homepage will show ~900 real dealer listings with photos.

---

## Project Structure

```
cargrab/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app — CORS, rate limiting, router
│   │   ├── config.py            # All config from environment variables
│   │   ├── database.py          # Async SQLAlchemy engine
│   │   ├── models/              # ORM models (7 tables)
│   │   │   ├── listing.py       # Core listings table
│   │   │   ├── vehicle.py       # VIN-decoded specs (cached)
│   │   │   ├── user.py
│   │   │   ├── source.py
│   │   │   ├── photo.py
│   │   │   ├── price_history.py
│   │   │   └── saved_search.py  # SavedSearch + PriceAlert
│   │   ├── schemas/             # Pydantic DTOs
│   │   ├── api/v1/              # Route handlers
│   │   │   ├── listings.py      # Search + detail
│   │   │   ├── search.py        # Suggestions + facets
│   │   │   ├── vin.py           # NHTSA VIN decode
│   │   │   ├── auth.py          # Register / login / refresh / me
│   │   │   └── saved_searches.py# Saved searches + price alerts
│   │   ├── services/
│   │   │   ├── listing_service.py
│   │   │   ├── vin_service.py   # NHTSA decode + recall count
│   │   │   ├── cache_service.py # Redis get-or-set
│   │   │   └── auth_service.py  # JWT + bcrypt
│   │   └── tasks/
│   │       ├── celery_app.py
│   │       ├── beat_schedule.py # Cron schedule
│   │       └── ingest.py        # Upsert listings + price history
│   ├── scraper/
│   │   ├── base.py              # BaseSource ABC + RawListing
│   │   ├── normalizer.py        # RawListing → DB-ready dict
│   │   ├── autodev.py           # Auto.dev dealer inventory API (free tier)
│   │   ├── ebay.py              # eBay Motors Browse API (free)
│   │   ├── carmax.py            # CarMax Playwright scraper (residential IP req'd)
│   │   ├── marketcheck.py       # MarketCheck API poller
│   │   └── carvana.py           # Stub (awaiting credentials)
│   ├── seed.py                  # 30 realistic demo listings for local dev
│   ├── migrations/              # Alembic migration files
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── app/
│       │   ├── page.tsx         # Home — hero + featured grids
│       │   ├── search/          # Search page (filter sidebar + results)
│       │   ├── listing/[id]/    # Listing detail (gallery, specs, chart)
│       │   └── saved/           # Saved searches (auth-gated)
│       ├── components/
│       │   ├── ui/              # GlassCard, Button, Badge, Input, Spinner
│       │   ├── layout/          # Navbar, Footer
│       │   ├── listings/        # ListingCard, ListingGrid, PhotoGallery,
│       │   │                    # SpecTable, PriceHistoryChart
│       │   └── search/          # HeroSearch, FilterSidebar, SortBar
│       ├── lib/
│       │   ├── api.ts           # Typed fetch wrappers for all endpoints
│       │   └── formatters.ts    # formatPrice, formatMileage, etc.
│       └── types/index.ts       # All shared TypeScript interfaces
├── docker-compose.yml
├── .env.example
├── CLAUDE.md                    # Developer guide for Claude Code
└── README.md
```

---

## API Reference

All endpoints live at `http://localhost:8000/api/v1/`. The full interactive docs are at `/api/docs`.

### Listings

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/listings` | Search listings — supports `make`, `model`, `year_min/max`, `price_min/max` (cents), `mileage_max`, `condition`, `state`, `query`, `sort`, `page`, `page_size` |
| `GET` | `/listings/featured` | 8 newest listings (homepage) |
| `GET` | `/listings/{id}` | Full detail — photos, specs, price history |

### Search helpers

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/search/suggestions?q=` | Make/model autocomplete |
| `GET` | `/search/facets` | Count per make / state / condition |
| `GET` | `/vin/{vin}` | Decode VIN via NHTSA + recall count |

### Auth

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/auth/register` | `{email, password}` → tokens |
| `POST` | `/auth/login` | `{email, password}` → tokens |
| `POST` | `/auth/refresh` | `Authorization: Bearer <refresh_token>` → new tokens |
| `GET` | `/auth/me` | Current user (JWT required) |

### Saved features *(JWT required)*

| Method | Path | Description |
|--------|------|-------------|
| `GET/POST` | `/saved-searches` | List or create saved searches |
| `DELETE` | `/saved-searches/{id}` | Delete a saved search |
| `GET/POST` | `/alerts` | List or create price alerts |
| `DELETE` | `/alerts/{id}` | Delete an alert |

---

## Data Sources

| Source | Type | Cost | Status | Notes |
|--------|------|------|--------|-------|
| **Auto.dev** | Licensed API | Free (1k calls/mo) | Active | Best free source. Real dealer inventory. Set `AUTODEV_API_KEY`. Sign up at [auto.dev](https://auto.dev) |
| **eBay Motors** | Official API | Free | Active | Private + dealer listings. Set `EBAY_APP_ID` + `EBAY_CERT_ID`. Register at [developer.ebay.com](https://developer.ebay.com) |
| **CarMax** | Unofficial API | Free | Blocked | Blocked by Akamai on cloud/Docker IPs. Works from residential ISP. |
| **MarketCheck** | Licensed API | ~$200–$2k/mo | Key-gated | Set `MARKETCHECK_API_KEY` in `.env` to enable. |
| **NHTSA** | Government API | Free | Active | VIN decode + safety recalls. No key. Permanently cached by VIN. |
| **CarAPI** | Public API | Free | Active | Make/model/trim database powering search autocomplete. No key needed. |
| **Carvana** | Partner API | TBD | Stub | Set `CARVANA_API_KEY` when partner access is obtained. |

**Priority order**: Auto.dev → eBay Motors → MarketCheck (paid) → CarMax (residential IP only)

**Off-limits for scraping**: Autotrader, Cars.com, CarGurus, Craigslist — all have active ToS enforcement with precedent ($31M+ settlements).

> **CarMax + Akamai**: CarMax's search API is protected by Akamai Bot Manager, which blocks all requests from cloud/Docker IP ranges (including residential VPS providers). The Playwright-based scraper in `scraper/carmax.py` will work from a home internet connection but not from any cloud host. Use the seed script for dev/demo.

---

## Prices are stored in cents

All `price` values in the database and API are **integer cents** (e.g. $24,500 → `2450000`). The API response includes both `price: 2450000` and a computed `price_formatted: "$24,500"` field.

---

## Polling Schedule

| Task | Interval | Notes |
|------|----------|-------|
| Poll Auto.dev | Every 60 minutes | Conserves free-tier quota (1k calls/month) |
| Poll eBay Motors | Every 30 minutes | Free developer tier |
| Poll CarMax | Every 30 minutes | Requires residential IP to pass Akamai |
| Poll MarketCheck | Every 15 minutes | Requires paid API key |
| Check price alerts | Every 5 minutes | |

---

## Adding a New Data Source

1. Create `backend/scraper/mysource.py` extending `BaseSource`
2. Implement `async def fetch(self) -> list[RawListing]`
3. Add a Celery task in `backend/app/tasks/ingest.py`
4. Register it in `backend/app/tasks/beat_schedule.py`
5. Insert a row into the `sources` table

---

## Environment Variables

Copy `.env.example` to `.env`. All defaults work for local dev.

| Variable | Required | Description |
|----------|----------|-------------|
| `POSTGRES_PASSWORD` | Yes | Postgres password |
| `DATABASE_URL` | Yes | Full asyncpg connection string |
| `REDIS_URL` | Yes | Redis connection string |
| `JWT_SECRET_KEY` | Yes | **Change for production** |
| `CORS_ORIGINS` | Yes | JSON array: `["http://localhost:3000"]` |
| `AUTODEV_API_KEY` | No | Enables Auto.dev dealer inventory (free tier: 1k calls/month) |
| `EBAY_APP_ID` | No | eBay Motors App ID — free developer account at developer.ebay.com |
| `EBAY_CERT_ID` | No | eBay Motors Cert ID (required alongside App ID) |
| `MARKETCHECK_API_KEY` | No | Enables MarketCheck listings (paid) |
| `CARVANA_API_KEY` | No | Enables Carvana listings |
| `SENTRY_DSN` | No | Error tracking |

---

## Production Deployment

This project is designed to run on a VPS via Docker Compose.

1. Add a `caddy` service to `docker-compose.yml` for TLS + reverse proxy
2. Set `JWT_SECRET_KEY` to a strong random value (`openssl rand -hex 32`)
3. Change the backend command from `uvicorn --reload` to `gunicorn -k uvicorn.workers.UvicornWorker`
4. Set `CORS_ORIGINS` to your production domain

---

## License

MIT
