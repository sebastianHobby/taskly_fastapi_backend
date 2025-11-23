import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class CorsSettings(BaseSettings):
    """Application settings."""

    allow_origins: list[str] = ["http://localhost:8081", "https://localhost:8081"]
    allow_credentials: bool = True
    allow_headers: str = "*"
    allow_methods: str = "*"


DOTENV = os.path.join(os.path.dirname(__file__), ".env")


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=DOTENV)
    database_url: str
    PROJECT_NAME: str = "Taskly FastAPI"
    DEBUG: bool = False
    cors: CorsSettings = CorsSettings()


settings = Settings()
