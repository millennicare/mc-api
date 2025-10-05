from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
    database_url: str = Field(validation_alias="DATABASE_URL")


database_settings = DatabaseSettings()
