from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    crm_api_url: Optional[str] = None
    crm_email: Optional[str] = None
    crm_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    google_cloud_project: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "allow"  # Allow extra fields not defined in the model


settings = Settings()
