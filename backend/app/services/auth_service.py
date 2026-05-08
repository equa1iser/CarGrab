import asyncio
import secrets
import uuid
from datetime import datetime, timedelta, timezone

import httpx
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _make_token(data: dict, expires_delta: timedelta) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + expires_delta
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(user_id: uuid.UUID) -> str:
    return _make_token(
        {"sub": str(user_id), "type": "access"},
        timedelta(minutes=settings.access_token_expire_minutes),
    )


def create_refresh_token(user_id: uuid.UUID) -> str:
    return _make_token(
        {"sub": str(user_id), "type": "refresh"},
        timedelta(days=settings.refresh_token_expire_days),
    )


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return {}


async def get_user_by_email(email: str, db: AsyncSession) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(user_id: uuid.UUID, db: AsyncSession) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_google_id(google_id: str, db: AsyncSession) -> User | None:
    result = await db.execute(select(User).where(User.google_id == google_id))
    return result.scalar_one_or_none()


async def verify_google_token(credential: str) -> dict | None:
    """Verify a Google ID token via Google's tokeninfo endpoint."""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"id_token": credential},
        )
    if resp.status_code != 200:
        return None
    data = resp.json()
    if data.get("aud") != settings.google_client_id:
        return None
    return data  # keys: sub, email, name, picture, email_verified


def generate_reset_token() -> str:
    return secrets.token_urlsafe(32)


async def store_reset_token(email: str, token: str) -> None:
    from app.services.cache_service import cache_set
    await cache_set(f"reset:{token}", email, ttl=3600)


async def consume_reset_token(token: str) -> str | None:
    """Return the email if the token is valid, then delete it (one-time use)."""
    from app.services.cache_service import cache_get, get_redis
    email = await cache_get(f"reset:{token}")
    if email:
        r = get_redis()
        await r.delete(f"cargrab:reset:{token}")
    return email
