from fastapi import APIRouter, HTTPException, Depends
from typing import List

from src.api.schemas import DriverCreate, DriverOut
from src.api.models import DRIVERS, DriverProfile, Role
from src.api.models import gen_id
from src.api.auth import require_role

router = APIRouter(prefix="/drivers", tags=["Drivers"])


@router.post("", summary="Create or update driver profile", response_model=DriverOut)
def upsert_driver_profile(body: DriverCreate, user=Depends(require_role(Role.DRIVER))):
    """Create or update the driver profile for the current user."""
    # upsert
    existing = next((d for d in DRIVERS.values() if d.user_id == user.id), None)
    if existing:
        existing.vehicle_number = body.vehicle_number
        existing.license_id = body.license_id
        return DriverOut(**existing.__dict__)
    profile = DriverProfile(
        id=gen_id(),
        user_id=user.id,
        vehicle_number=body.vehicle_number,
        license_id=body.license_id,
    )
    DRIVERS[profile.id] = profile
    return DriverOut(**profile.__dict__)


@router.get("", summary="List drivers", response_model=List[DriverOut])
def list_drivers():
    """List all active driver profiles."""
    return [DriverOut(**d.__dict__) for d in DRIVERS.values() if d.is_active]


@router.post("/{driver_id}/toggle", summary="Toggle driver availability", response_model=DriverOut)
def toggle_driver(driver_id: str, user=Depends(require_role(Role.DRIVER))):
    """Enable/Disable the driver profile (only owner driver)."""
    profile = DRIVERS.get(driver_id)
    if not profile or profile.user_id != user.id:
        raise HTTPException(status_code=404, detail="Driver not found")
    profile.is_active = not profile.is_active
    return DriverOut(**profile.__dict__)
