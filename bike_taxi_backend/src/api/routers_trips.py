from fastapi import APIRouter, HTTPException, Depends
from typing import List

from src.api.schemas import TripUpdateIn, TripUpdateOut
from src.api.models import TRIPS, TripUpdate, RIDES, RideStatus, Role
from src.api.models import gen_id
from src.api.auth import require_role

router = APIRouter(prefix="/trips", tags=["Trip Tracking"])


@router.post("/{ride_id}/updates", summary="Post trip update", response_model=TripUpdateOut)
def post_trip_update(ride_id: str, body: TripUpdateIn, user=Depends(require_role(Role.DRIVER))):
    """Driver posts live trip updates (location, speed)."""
    ride = RIDES.get(ride_id)
    if not ride or ride.driver_id != user.id or ride.status != RideStatus.IN_PROGRESS:
        raise HTTPException(status_code=404, detail="Ride not found or not active")
    upd = TripUpdate(id=gen_id(), ride_id=ride_id, lat=body.lat, lng=body.lng, speed_kmh=body.speed_kmh, note=body.note)
    TRIPS.setdefault(ride_id, []).append(upd)
    return TripUpdateOut(**upd.__dict__)


@router.get("/{ride_id}/updates", summary="List trip updates", response_model=List[TripUpdateOut])
def list_trip_updates(ride_id: str, user=Depends(require_role(Role.PASSENGER))):
    """Passenger fetches trip updates for their ride."""
    ride = RIDES.get(ride_id)
    if not ride or ride.passenger_id != user.id:
        raise HTTPException(status_code=404, detail="Ride not found")
    return [TripUpdateOut(**u.__dict__) for u in TRIPS.get(ride_id, [])]
