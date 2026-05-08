from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.vehicle import VehicleResponse
from app.services import vin_service

router = APIRouter(prefix="/vin", tags=["vin"])


@router.get("/{vin}", response_model=VehicleResponse)
async def decode(vin: str, db: AsyncSession = Depends(get_db)):
    vehicle = await vin_service.decode_vin(vin, db)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Could not decode VIN")
    return VehicleResponse.model_validate(vehicle)
