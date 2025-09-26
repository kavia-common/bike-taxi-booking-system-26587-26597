from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.config import settings
from src.api.routers_auth import router as auth_router
from src.api.routers_drivers import router as drivers_router
from src.api.routers_rides import router as rides_router
from src.api.routers_trips import router as trips_router
from src.api.routers_payments import router as payments_router

openapi_tags = [
    {"name": "Health", "description": "Service health and metadata"},
    {"name": "Authentication", "description": "User registration and login"},
    {"name": "Drivers", "description": "Driver profile management and availability"},
    {"name": "Rides", "description": "Ride booking and lifecycle"},
    {"name": "Trip Tracking", "description": "Live trip updates"},
    {"name": "Payments", "description": "Payment initiation and callbacks"},
]

app = FastAPI(
    title=settings.app_name,
    description="Backend service for Bike Taxi Booking System. Provides REST APIs for auth, rides, drivers, trips, and payments.",
    version=settings.api_version,
    openapi_tags=openapi_tags,
)

# CORS
allow_origins = ["*"] if settings.cors_allow_origins.strip() == "*" else [o.strip() for o in settings.cors_allow_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health and meta
@app.get("/", tags=["Health"], summary="Health Check")
def health_check():
    """Check service health and version."""
    return {"message": "Healthy", "version": settings.api_version, "name": settings.app_name}

# WebSocket usage helper (no actual websocket in this implementation)
@app.get("/ws-info", tags=["Health"], summary="WebSocket usage help")
def websocket_usage_info():
    """Provides information about WebSocket endpoints and usage.
    Note: This service currently does not expose a WebSocket endpoint. Real-time tracking can be implemented in the future.
    """
    return {
        "websocket_endpoints": [],
        "note": "No WebSocket endpoints currently. Use /trips/{ride_id}/updates GET to poll trip updates."
    }

# Routers
app.include_router(auth_router)
app.include_router(drivers_router)
app.include_router(rides_router)
app.include_router(trips_router)
app.include_router(payments_router)
