from fastapi import APIRouter, HTTPException, Depends
from typing import List

from src.api.schemas import RideRequest, RideOut
from src.api.models import RIDES, Ride, RideStatus, Role, DRIVERS
from src.api.models import gen_id
from src.api.auth import require_role

router = APIRouter(prefix="/rides", tags=["Rides"])


def _estimate_fare(pickup_lat: float, pickup_lng: float, dropoff_lat: float, dropoff_lng: float) -> float:
    # Simple distance approximation for demo, not accurate
    dist = abs(pickup_lat - dropoff_lat) + abs(pickup_lng - dropoff_lng)
    base = 2.0
    per_km = 1.5
    return round(base + per_km * dist * 111, 2)  # 1 degree ~ 111km


@router.post("", summary="Book a ride", response_model=RideOut, status_code=201)
def book_ride(body: RideRequest, user=Depends(require_role(Role.PASSENGER))):
    """Passenger books a new ride; system computes fare estimate."""
    ride = Ride(
        id=gen_id(),
        passenger_id=user.id,
        driver_id=None,
        pickup_lat=body.pickup_lat,
        pickup_lng=body.pickup_lng,
        dropoff_lat=body.dropoff_lat,
        dropoff_lng=body.dropoff_lng,
        status=RideStatus.REQUESTED,
        fare_estimate=_estimate_fare(body.pickup_lat, body.pickup_lng, body.dropoff_lat, body.dropoff_lng),
    )
    RIDES[ride.id] = ride
    return RideOut(
        id=ride.id,
        passenger_id=ride.passenger_id,
        driver_id=ride.driver_id,
        pickup_lat=ride.pickup_lat,
        pickup_lng=ride.pickup_lng,
        dropoff_lat=ride.dropoff_lat,
        dropoff_lng=ride.dropoff_lng,
        status=ride.status.value,
        fare_estimate=ride.fare_estimate,
        created_at=ride.created_at,
        fare_final=ride.fare_final,
    )


@router.post("/{ride_id}/accept", summary="Driver accepts ride", response_model=RideOut)
def accept_ride(ride_id: str, user=Depends(require_role(Role.DRIVER))):
    """Driver accepts an available ride."""
    ride = RIDES.get(ride_id)
    if not ride or ride.status != RideStatus.REQUESTED:
        raise HTTPException(status_code=404, detail="Ride not available")
    # ensure driver profile exists and active
    profile = next((d for d in DRIVERS.values() if d.user_id == user.id and d.is_active), None)
    if not profile:
        raise HTTPException(status_code=400, detail="Active driver profile required")
    ride.driver_id = user.id
    ride.status = RideStatus.ACCEPTED
    return RideOut(**{
        "id": ride.id,
        "passenger_id": ride.passenger_id,
        "driver_id": ride.driver_id,
        "pickup_lat": ride.pickup_lat,
        "pickup_lng": ride.pickup_lng,
        "dropoff_lat": ride.dropoff_lat,
        "dropoff_lng": ride.dropoff_lng,
        "status": ride.status.value,
        "fare_estimate": ride.fare_estimate,
        "fare_final": ride.fare_final,
        "created_at": ride.created_at
    })


@router.post("/{ride_id}/start", summary="Start ride", response_model=RideOut)
def start_ride(ride_id: str, user=Depends(require_role(Role.DRIVER))):
    """Driver starts the ride after acceptance."""
    ride = RIDES.get(ride_id)
    if not ride or ride.status != RideStatus.ACCEPTED or ride.driver_id != user.id:
        raise HTTPException(status_code=404, detail="Ride not found or not accepted by driver")
    ride.status = RideStatus.IN_PROGRESS
    return RideOut(**{**ride.__dict__, "status": ride.status.value})


@router.post("/{ride_id}/complete", summary="Complete ride", response_model=RideOut)
def complete_ride(ride_id: str, user=Depends(require_role(Role.DRIVER))):
    """Driver completes the ride; set final fare to estimate for demo."""
    ride = RIDES.get(ride_id)
    if not ride or ride.status != RideStatus.IN_PROGRESS or ride.driver_id != user.id:
        raise HTTPException(status_code=404, detail="Ride not found or not in progress")
    ride.status = RideStatus.COMPLETED
    ride.fare_final = ride.fare_estimate
    return RideOut(**{**ride.__dict__, "status": ride.status.value})


@router.post("/{ride_id}/cancel", summary="Cancel ride", response_model=RideOut)
def cancel_ride(ride_id: str, user=Depends(require_role(Role.PASSENGER))):
    """Passenger cancels their ride if not started."""
    ride = RIDES.get(ride_id)
    if not ride or ride.passenger_id != user.id:
        raise HTTPException(status_code=404, detail="Ride not found")
    if ride.status in (RideStatus.IN_PROGRESS, RideStatus.COMPLETED):
        raise HTTPException(status_code=400, detail="Cannot cancel after ride started")
    ride.status = RideStatus.CANCELLED
    return RideOut(**{**ride.__dict__, "status": ride.status.value})


@router.get("", summary="List my rides", response_model=List[RideOut])
def list_my_rides(user=Depends(require_role(Role.PASSENGER))):
    """Passenger lists their ride history."""
    rides = [r for r in RIDES.values() if r.passenger_id == user.id]
    return [RideOut(**{**r.__dict__, "status": r.status.value}) for r in rides]


@router.get("/{ride_id}", summary="Get ride", response_model=RideOut)
def get_ride(ride_id: str, user=Depends(require_role(Role.PASSENGER))):
    """Get a single ride by id (must be the passenger)."""
    ride = RIDES.get(ride_id)
    if not ride or ride.passenger_id != user.id:
        raise HTTPException(status_code=404, detail="Ride not found")
    return RideOut(**{**ride.__dict__, "status": ride.status.value})
