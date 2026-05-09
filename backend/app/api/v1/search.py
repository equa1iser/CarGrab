import json

import anthropic
import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.listing import Listing
from app.services import listing_service
from app.services.cache_service import cache_get, cache_set

router = APIRouter(prefix="/search", tags=["search"])

_AI_SYSTEM_PROMPT = """You are a car search assistant. Extract structured filters from a natural language car search query.
Return ONLY a valid JSON object with these optional fields:
  make: string (car manufacturer, e.g. "Toyota", "Ford", "BMW")
  model: string (car model, e.g. "Camry", "F-150", "3 Series")
  year_min: integer (minimum model year, inclusive)
  year_max: integer (maximum model year, inclusive)
  price_min: integer (minimum price in CENTS, e.g. $20,000 = 2000000)
  price_max: integer (maximum price in CENTS, e.g. $90,000 = 9000000)
  mileage_max: integer (maximum mileage in miles)
  condition: one of "used", "certified", or "salvage"
  state: string (2-letter US state abbreviation, e.g. "CA", "TX")
  query: string (remaining descriptive terms not captured above, such as color, drivetrain type like "4WD" or "AWD", body style, or features)
  explanation: string (brief human-readable summary of what you understood, e.g. "Ford F-150 trucks with 4WD, built before 2022, under $90,000")

Rules:
- Only include fields that are explicitly mentioned or strongly implied by the query
- Prices must always be converted to cents (multiply dollar amount by 100)
- "before 2022" means year_max: 2022, "after 2015" means year_min: 2015
- "under $90K" or "less than $90,000" means price_max: 9000000
- Always include an explanation field
- Return ONLY the JSON object — no markdown, no code fences, no other text"""


class AiSearchRequest(BaseModel):
    query: str


@router.post("/ai")
async def ai_search(body: AiSearchRequest):
    if not settings.anthropic_api_key:
        raise HTTPException(status_code=503, detail="AI search is not configured on this server.")

    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    try:
        message = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            system=_AI_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": body.query}],
        )
        raw = message.content[0].text.strip()
        data = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail="AI returned an unexpected response. Please try rephrasing your query.")
    except anthropic.APIError as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {e}")

    explanation = data.pop("explanation", None)
    return {"filters": data, "explanation": explanation}

_CARAPI_BASE = "https://carapi.app/api"
_CARAPI_MAKES_TTL = 86400   # cache for 24 h — make list is stable
_CARAPI_MODELS_TTL = 86400


def _parse_carapi_list(data) -> list[str]:
    """CarAPI wraps results in {data: [...]} — unwrap and extract name strings."""
    if isinstance(data, dict):
        items = data.get("data") or []
    elif isinstance(data, list):
        items = data
    else:
        return []
    if not items:
        return []
    if isinstance(items[0], dict):
        return [m["name"] for m in items if m.get("name")]
    return [str(m) for m in items if m]


async def _carapi_makes() -> list[str]:
    cached = await cache_get("carapi:makes")
    if cached:
        return cached

    makes: list[str] = []
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # All ~68 makes fit in one request at limit=100
            resp = await client.get(
                f"{_CARAPI_BASE}/makes",
                params={"verbose": "yes", "limit": 100},
            )
            resp.raise_for_status()
            makes = _parse_carapi_list(resp.json())
    except Exception:
        pass

    if makes:
        await cache_set("carapi:makes", makes, ttl=_CARAPI_MAKES_TTL)
    return makes


async def _carapi_models(make: str) -> list[str]:
    key = f"carapi:models:{make.lower()}"
    cached = await cache_get(key)
    if cached:
        return cached

    models: list[str] = []
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{_CARAPI_BASE}/models/v2",
                params={"make": make, "limit": 200},
            )
            resp.raise_for_status()
            models = _parse_carapi_list(resp.json())
    except Exception:
        pass

    if models:
        await cache_set(key, models, ttl=_CARAPI_MODELS_TTL)
    return models


@router.get("/suggestions")
async def suggestions(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    q_lower = q.lower()

    # Always query the DB first — these are real listings the user can actually browse
    db_makes_rows = await db.execute(
        select(distinct(Listing.make))
        .where(Listing.is_active == True, func.lower(Listing.make).contains(q_lower))  # noqa: E712
        .limit(10)
    )
    db_models_rows = await db.execute(
        select(distinct(Listing.model))
        .where(Listing.is_active == True, func.lower(Listing.model).contains(q_lower))  # noqa: E712
        .limit(10)
    )
    db_makes = [r[0] for r in db_makes_rows if r[0]]
    db_models = [r[0] for r in db_models_rows if r[0]]

    # Supplement with CarAPI for broader autocomplete coverage
    api_makes = [m for m in await _carapi_makes() if q_lower in m.lower()][:10]

    # Fetch models from CarAPI when the query matches a make name
    api_models: list[str] = []
    if len(q) >= 3:
        # Check if query matches any known make (DB or CarAPI)
        matched_makes = _merge_unique(db_makes, api_makes, limit=3)
        for make_name in matched_makes:
            make_models = await _carapi_models(make_name)
            api_models.extend(make_models)
        # Also check if the query itself is a partial model search in the DB
        # (already captured in db_models above)

    # Merge: DB results first (they have actual listings), then CarAPI extras
    makes = _merge_unique(db_makes, api_makes, limit=10)
    models = _merge_unique(db_models, api_models, limit=10)

    return {"makes": makes, "models": models}


def _merge_unique(primary: list[str], secondary: list[str], limit: int) -> list[str]:
    seen = set()
    result = []
    for item in primary + secondary:
        if item and item.lower() not in seen and len(result) < limit:
            seen.add(item.lower())
            result.append(item)
    return result


@router.get("/facets")
async def facets(db: AsyncSession = Depends(get_db)):
    return await listing_service.get_search_facets(db)
