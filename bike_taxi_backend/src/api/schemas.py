from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum


# PUBLIC_INTERFACE
class Token(BaseModel):
    """JWT Access token response."""
    access_token: str = Field(..., description="JWT bearer token")
    token_type: str = Field(default="bearer", description="Type of token (bearer)")
    expires_in: int = Field(..., description="Expiration in seconds")


class Role(str, Enum):
    passenger = "passenger"
    driver = "driver"
    admin = "admin"


# PUBLIC_INTERFACE
class UserCreate(BaseModel):
    """Request body for user registration."""
    email: EmailStr = Field(..., description="User email")
    name: str = Field(..., min_length=1, description="Full name")
    password: str = Field(..., min_length=6, description="Password")
    role: Role = Field(default=Role.passenger, description="Role of the user")


# PUBLIC_INTERFACE
class UserLogin(BaseModel):
    """Request body for user login."""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=6, description="Password")


# PUBLIC_INTERFACE
class UserOut(BaseModel):
    """User info response (safe for clients)."""
    id: str
    email: EmailStr
    name: str
    role: Role
    created_at: datetime


# PUBLIC_INTERFACE
class DriverCreate(BaseModel):
    """Create or update driver profile for a user with driver role."""
    vehicle_number: str = Field(..., min_length=3, description="Vehicle number/plate")
    license_id: str = Field(..., min_length=3, description="Driver license id")


# PUBLIC_INTERFACE
class DriverOut(BaseModel):
    """Driver profile details."""
    id: str
    user_id: str
    vehicle_number: str
    license_id: str
    is_active: bool
    rating: float
    total_rides: int
    created_at: datetime


# PUBLIC_INTERFACE
class RideRequest(BaseModel):
    """Ride booking request details."""
    pickup_lat: float = Field(..., description="Pickup latitude")
    pickup_lng: float = Field(..., description="Pickup longitude")
    dropoff_lat: float = Field(..., description="Dropoff latitude")
    dropoff_lng: float = Field(..., description="Dropoff longitude")


# PUBLIC_INTERFACE
class RideOut(BaseModel):
    """Ride details for client display."""
    id: str
    passenger_id: str
    driver_id: Optional[str] = None
    pickup_lat: float
    pickup_lng: float
    dropoff_lat: float
    dropoff_lng: float
    status: str
    fare_estimate: Optional[float] = None
    fare_final: Optional[float] = None
    created_at: datetime


# PUBLIC_INTERFACE
class TripUpdateIn(BaseModel):
    """Trip live location update."""
    lat: float
    lng: float
    speed_kmh: Optional[float] = None
    note: Optional[str] = None


# PUBLIC_INTERFACE
class TripUpdateOut(BaseModel):
    """Trip update response payload."""
    id: str
    ride_id: str
    lat: float
    lng: float
    speed_kmh: Optional[float] = None
    note: Optional[str] = None
    timestamp: datetime


# PUBLIC_INTERFACE
class PaymentInit(BaseModel):
    """Initiate payment for a ride."""
    ride_id: str = Field(..., description="Ride identifier")


# PUBLIC_INTERFACE
class PaymentOut(BaseModel):
    """Payment details response."""
    id: str
    ride_id: str
    amount: float
    currency: str
    status: str
    provider_ref: Optional[str] = None
    created_at: datetime
