from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    secret_key: str
    algorithm: str = "HS256"
    database_url: str 
    frontend_origins: List[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"                                  # Ignores extra variables in the .env file so it doesn't crash
    )
settings = Settings()