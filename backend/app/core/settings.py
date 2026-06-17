import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database related settings
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "ascc"
    DB_USER: str = "ascc"
    DB_PASSWORD: str = "ascc_root"

    # Logging related settings
    LOG_LEVEL: str = "DEBUG"

settings = Settings()
