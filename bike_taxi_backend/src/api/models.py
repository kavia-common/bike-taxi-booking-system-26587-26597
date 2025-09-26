from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, List
from datetime import datetime
import uuid


class Role(str, Enum):
    PASSENGER = "passenger"
    DRIVER = "driver"
    ADMIN = "admin"


class RideStatus(str, Enum):
    REQUESTED = "requested"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    FAILED = "failed"
    REFUNDED = "refunded"


@dataclass
class User:
    id: str
    email: str
    name: str
    role: Role
    hashed_password: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DriverProfile:
    id: str
    user_id: str
    vehicle_number: str
    license_id: str
    is_active: bool = True
    rating: float = 5.0
    total_rides: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Ride:
    id: str
    passenger_id: str
    driver_id: Optional[str]
    pickup_lat: float
    pickup_lng: float
    dropoff_lat: float
    dropoff_lng: float
    status: RideStatus = RideStatus.REQUESTED
    fare_estimate: Optional[float] = None
    fare_final: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TripUpdate:
    id: str
    ride_id: str
    lat: float
    lng: float
    speed_kmh: Optional[float] = None
    note: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Payment:
    id: str
    ride_id: str
    amount: float
    currency: str = "USD"
    status: PaymentStatus = PaymentStatus.PENDING
    provider_ref: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


# In-memory stores (placeholder for bike_taxi_database)
USERS: Dict[str, User] = {}
DRIVERS: Dict[str, DriverProfile] = {}
RIDES: Dict[str, Ride] = {}
TRIPS: Dict[str, List[TripUpdate]] = {}
PAYMENTS: Dict[str, Payment] = {}


def gen_id() -> str:
    return uuid.uuid4().hex
