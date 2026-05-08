import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    GoogleAuthRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.services import auth_service
from app.services import email_service

router = APIRouter(prefix="/auth", tags=["auth"])


async def current_user(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ", 1)[1]
    payload = auth_service.decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = await auth_service.get_user_by_id(uuid.UUID(payload["sub"]), db)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await auth_service.get_user_by_email(body.email, db)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(
        email=body.email,
        hashed_pw=auth_service.hash_password(body.password),
    )
    db.add(user)
    await db.flush()
    return TokenResponse(
        access_token=auth_service.create_access_token(user.id),
        refresh_token=auth_service.create_refresh_token(user.id),
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await auth_service.get_user_by_email(body.email, db)
    if not user or not user.hashed_pw or not auth_service.verify_password(body.password, user.hashed_pw):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")
    return TokenResponse(
        access_token=auth_service.create_access_token(user.id),
        refresh_token=auth_service.create_refresh_token(user.id),
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing refresh token")
    token = authorization.split(" ", 1)[1]
    payload = auth_service.decode_token(token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user = await auth_service.get_user_by_id(uuid.UUID(payload["sub"]), db)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found")
    return TokenResponse(
        access_token=auth_service.create_access_token(user.id),
        refresh_token=auth_service.create_refresh_token(user.id),
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(current_user)):
    return UserResponse.model_validate(user)


@router.post("/forgot-password", status_code=204)
async def forgot_password(body: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    user = await auth_service.get_user_by_email(body.email, db)
    if user:
        token = auth_service.generate_reset_token()
        await auth_service.store_reset_token(body.email, token)
        await email_service.send_password_reset_email(body.email, token)
    # Always 204 — never reveal whether an email is registered
    return Response(status_code=204)


@router.post("/reset-password", status_code=204)
async def reset_password(body: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    if len(body.password) < 8:
        raise HTTPException(status_code=422, detail="Password must be at least 8 characters")
    email = await auth_service.consume_reset_token(body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired reset link")
    user = await auth_service.get_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    user.hashed_pw = auth_service.hash_password(body.password)
    await db.commit()
    return Response(status_code=204)


@router.post("/google", response_model=TokenResponse)
async def google_auth(body: GoogleAuthRequest, db: AsyncSession = Depends(get_db)):
    if not settings.google_client_id:
        raise HTTPException(status_code=501, detail="Google sign-in is not configured on this server")
    info = await auth_service.verify_google_token(body.credential)
    if not info:
        raise HTTPException(status_code=401, detail="Invalid Google credential")

    google_id: str = info["sub"]
    email: str = info["email"]

    # Find by Google ID first, then fall back to email (links existing accounts)
    user = await auth_service.get_user_by_google_id(google_id, db)
    if not user:
        user = await auth_service.get_user_by_email(email, db)
        if user:
            user.google_id = google_id
        else:
            user = User(email=email, google_id=google_id, is_verified=True)
            db.add(user)

    await db.flush()
    await db.commit()
    return TokenResponse(
        access_token=auth_service.create_access_token(user.id),
        refresh_token=auth_service.create_refresh_token(user.id),
        user=UserResponse.model_validate(user),
    )
