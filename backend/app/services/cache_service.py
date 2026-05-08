import hashlib
import json
from typing import Any, Awaitable, Callable

import redis.asyncio as aioredis

from app.config import settings

_redis: aioredis.Redis | None = None


def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _redis


def _make_key(namespace: str, params: dict) -> str:
    raw = json.dumps(params, sort_keys=True)
    digest = hashlib.sha256(raw.encode()).hexdigest()[:16]
    return f"cargrab:{namespace}:{digest}"


async def get_or_set(
    namespace: str,
    params: dict,
    factory: Callable[[], Awaitable[Any]],
    ttl: int = 300,
) -> Any:
    r = get_redis()
    key = _make_key(namespace, params)
    cached = await r.get(key)
    if cached:
        return json.loads(cached)
    value = await factory()
    await r.setex(key, ttl, json.dumps(value, default=str))
    return value


async def invalidate(namespace: str, params: dict) -> None:
    r = get_redis()
    key = _make_key(namespace, params)
    await r.delete(key)
