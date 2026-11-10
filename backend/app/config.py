"""Application configuration using pydantic-settings."""
from functools import lru_cache
from typing import Optional

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings  # type: ignore


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite+aiosqlite:///./lifeos.db"

    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080  # 7 days

    # BharatCode AI
    bharatcode_api_key: str = "mock-key"
    bharatcode_api_base: str = "https://api.bharatcode.ai/v1"
    ai_provider: str = "mock"  # "mock" | "bharatcode"

    # File uploads
    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 10

    # App
    app_name: str = "LifeOS"
    debug: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def is_postgresql(self) -> bool:
        return "postgresql" in self.database_url


@lru_cache()
def get_settings() -> Settings:
    return Settings()
