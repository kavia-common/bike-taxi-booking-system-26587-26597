from pydantic import BaseModel, Field
from typing import Optional
import os

# PUBLIC_INTERFACE
class Settings(BaseModel):
    """Application settings loaded from environment variables.

    Attributes:
        app_name: Name of the FastAPI application.
        api_version: Semantic version of the API.
        cors_allow_origins: Comma-separated origins allowed for CORS.
        jwt_secret_key: Secret key for signing JWT tokens. REQUIRED at runtime.
        jwt_algorithm: Algorithm for JWT signing.
        access_token_exp_minutes: Access token validity in minutes.
        site_url: Base site URL used for auth redirects and callbacks.
        payment_provider_secret: Secret/token for verifying payment callbacks.
    """
    app_name: str = Field(default="Bike Taxi Backend", description="Name of the application")
    api_version: str = Field(default="1.0.0", description="API version")
    cors_allow_origins: str = Field(default="*", description="Comma-separated origins for CORS")
    jwt_secret_key: str = Field(default_factory=lambda: os.getenv("JWT_SECRET_KEY", ""), description="JWT secret")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_exp_minutes: int = Field(default=60 * 24, description="Access token expiration in minutes")
    site_url: str = Field(default_factory=lambda: os.getenv("SITE_URL", "http://localhost:3000"), description="Site URL for redirects")
    payment_provider_secret: str = Field(default_factory=lambda: os.getenv("PAYMENTS_WEBHOOK_SECRET", ""), description="Payment provider webhook secret")

    # Database placeholders - future agent should map to bike_taxi_database envs
    database_url: Optional[str] = Field(default_factory=lambda: os.getenv("DATABASE_URL"), description="Database URL (placeholder)")

settings = Settings()
