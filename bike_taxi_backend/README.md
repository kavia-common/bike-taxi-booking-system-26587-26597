# Bike Taxi Backend (FastAPI)

This service provides REST APIs for user authentication, ride booking and management, driver profiles, trip tracking, and payment processing callbacks.

Run locally:
- Install dependencies: pip install -r requirements.txt
- Set environment variables (.env): see .env.example
- Start server: uvicorn src.api.main:app --reload

Key endpoints (see /docs for full list):
- POST /auth/register, POST /auth/login
- GET /auth/users (demo listing)
- Driver: POST /drivers, GET /drivers, POST /drivers/{driver_id}/toggle
- Rides: POST /rides, POST /rides/{ride_id}/accept, POST /rides/{ride_id}/start, POST /rides/{ride_id}/complete, POST /rides/{ride_id}/cancel, GET /rides, GET /rides/{ride_id}
- Trips: POST /trips/{ride_id}/updates, GET /trips/{ride_id}/updates
- Payments: POST /payments/init, POST /payments/webhook

Notes:
- Data is stored in-memory for demo. Future integration with `bike_taxi_database` should replace in-memory stores in src/api/models.py.
- JWT signing uses HS256-like HMAC via custom implementation for demo purposes; replace with PyJWT/bcrypt in production.
