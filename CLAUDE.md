# CarGrab — Claude Code Guide

## Project Overview
CarGrab is a used car listing aggregator. It pulls listings from multiple sources (CarMax, MarketCheck, Carvana) into one searchable interface. The backend is also designed to serve a future mobile app.

## Environment Setup

### Python (Backend)
- Use the **conda `car` environment** (Python 3.12) for all backend work
- Never create a new venv — the conda env is the authoritative Python environment
- Activate: `conda activate car`
- Install deps: `pip install -r backend/requirements.txt`

### Node.js (Frontend)
- Requires Node.js **18+** (v24 is installed via winget)
- If the shell PATH still shows v16, use the full path: `"/c/Program Files/nodejs/npm.cmd"`
- After opening a new terminal, `node --version` should return v24+

### Docker
- All services run via Docker Compose
- Start infrastructure: `docker compose up postgres redis -d`
- Start full stack: `docker compose up -d`
- Rebuild after code changes: `docker compose up backend celery -d --build`

## Running the Stack

```bash
# Start all services
docker compose up -d

# Frontend dev server (separate terminal)
cd frontend && npm run dev

# Apply DB migrations (only needed after schema changes)
cd backend && conda run -n car alembic upgrade head

# Manually trigger a data poll
docker exec cargrab-celery-1 celery -A app.tasks.celery_app call app.tasks.ingest.poll_carmax
```

## Services & Ports
| Service  | URL                          |
|----------|------------------------------|
| Frontend | http://localhost:3000        |
| Backend  | http://localhost:8000        |
| API Docs | http://localhost:8000/api/docs |
| Postgres | localhost:5432               |
| Redis    | localhost:6379               |

## Architecture

```
CarGrab/
├── backend/              # FastAPI (Python 3.12)
│   ├── app/
│   │   ├── main.py       # App factory, CORS, rate limiting
│   │   ├── config.py     # pydantic-settings (reads .env)
│   │   ├── database.py   # Async SQLAlchemy engine + get_db()
│   │   ├── models/       # SQLAlchemy ORM models (7 tables)
│   │   ├── schemas/      # Pydantic request/response DTOs
│   │   ├── api/v1/       # Route files (listings, search, vin, auth, saved)
│   │   ├── services/     # Business logic (listing, vin, cache, auth)
│   │   └── tasks/        # Celery workers (ingest, beat schedule)
│   ├── scraper/          # Data source pollers
│   │   ├── base.py       # BaseSource ABC + RawListing dataclass
│   │   ├── normalizer.py # Source-agnostic normalization
│   │   ├── carmax.py     # CarMax unofficial API (free)
│   │   ├── marketcheck.py# MarketCheck commercial API (key required)
│   │   └── carvana.py    # Carvana stub (awaiting credentials)
│   └── migrations/       # Alembic migrations
├── frontend/             # Next.js 15 + TypeScript + Tailwind v4
│   └── src/
│       ├── app/          # App Router pages
│       ├── components/   # UI, layout, listings, search components
│       ├── lib/          # api.ts, formatters.ts
│       └── types/        # Shared TypeScript interfaces
└── docker-compose.yml
```

## Database Schema

All prices stored as **cents** (integer). E.g. $24,500 = `2450000`.

Key tables:
- `listings` — core table, unique on `(source_id, external_id)`
- `vehicles` — VIN-decoded specs, cached permanently (never re-decoded)
- `sources` — carmax / marketcheck / carvana
- `photos` — linked to listings, first photo is `is_primary=true`
- `price_history` — appended every time a price changes
- `saved_searches` — user-owned, filters stored as JSONB
- `price_alerts` — triggers when `listing.price <= target_price`

## API Design

Versioned REST at `/api/v1/`. Public endpoints are open; user endpoints require `Authorization: Bearer <jwt>`.

### Key endpoints
```
GET  /api/v1/listings              # search + filter + paginate
GET  /api/v1/listings/featured     # 8 newest (homepage)
GET  /api/v1/listings/{id}         # full detail with photos + specs
GET  /api/v1/search/suggestions    # make/model autocomplete
GET  /api/v1/search/facets         # counts for sidebar filters
GET  /api/v1/vin/{vin}             # decode via NHTSA (free, cached)
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh
GET  /api/v1/auth/me               # JWT required
GET/POST/DELETE /api/v1/saved-searches
GET/POST/DELETE /api/v1/alerts
```

## Data Sources

| Source      | Cost     | Status   | Notes |
|-------------|----------|----------|-------|
| CarMax      | Free     | Active   | Unofficial API — disable if contacted legally |
| MarketCheck | ~$200–2k/mo | Key-gated | Set `MARKETCHECK_API_KEY` in `.env` |
| NHTSA       | Free     | Active   | VIN decode + recalls only, no listings |
| Carvana     | TBD      | Stub     | Set `CARVANA_API_KEY` when obtained |

**Never scrape**: Autotrader, Cars.com, CarGurus, Craigslist — all have active ToS enforcement and prior litigation.

## Frontend Design System

Matches the dark glassmorphism aesthetic of worldwideview (https://demo.worldwideview.dev):
- Background: `#050a15` (navy-950)
- Accents: `#22d3ee` (cyan-400)
- Glass panels: `backdrop-blur(16px)` + `rgba(13,21,40,0.7)`
- Fonts: Inter (UI), JetBrains Mono (prices/data)
- Animations: `fadeUp` stagger (60ms per card), `pulseCyan`

CSS design tokens live in `frontend/src/app/globals.css` under `@theme inline`.

## Adding a New Data Source

1. Create `backend/scraper/mysource.py` extending `BaseSource`
2. Implement `async def fetch(self) -> list[RawListing]`
3. Add a Celery task in `backend/app/tasks/ingest.py` (copy `poll_carmax`)
4. Add to beat schedule in `backend/app/tasks/beat_schedule.py`
5. Seed the `sources` table: `INSERT INTO sources (name, base_url) VALUES ('mysource', '...')`

## Common Tasks

### Add a DB column
```bash
cd backend
# Edit the model file
conda run -n car alembic revision --autogenerate -m "add column"
conda run -n car alembic upgrade head
docker compose restart backend celery
```

### Wipe and re-seed the database
```bash
docker compose down -v          # removes postgres_data volume
docker compose up postgres -d
cd backend && conda run -n car alembic upgrade head
# Then trigger a poll to re-populate
```

### Check Celery task status
```bash
docker compose logs celery -f
```

## Environment Variables

See `.env.example` for the full list. Key ones:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | asyncpg postgres connection string |
| `REDIS_URL` | Redis connection string |
| `JWT_SECRET_KEY` | **Change in production** — use `openssl rand -hex 32` |
| `CORS_ORIGINS` | JSON array string e.g. `["http://localhost:3000"]` |
| `MARKETCHECK_API_KEY` | Optional — enables MarketCheck listings |
| `CARVANA_API_KEY` | Optional — enables Carvana listings |

## Known Issues / Future Work

- **Auth UI**: The Sign In / Get Started buttons in the Navbar are wired to button stubs. NextAuth or a custom modal needs to be connected to `POST /api/v1/auth/login`.
- **Photo caching**: Photos are hot-linked from source CDNs. Add a Celery task to download primary photos to S3/R2 and populate a `photo_cached_url` column.
- **Mobile app**: The backend API is mobile-ready (JWT auth, versioned routes, proper CORS). Add the mobile app's origin to `CORS_ORIGINS` in `.env`.
- **Production deployment**: Add `caddy` service to `docker-compose.yml` for TLS termination. Swap `uvicorn --reload` for `gunicorn -k uvicorn.workers.UvicornWorker`.
