from fastapi import APIRouter

from app.api.v1 import auth, listings, saved_searches, search, vin

router = APIRouter()
router.include_router(auth.router)
router.include_router(listings.router)
router.include_router(search.router)
router.include_router(vin.router)
router.include_router(saved_searches.router)
