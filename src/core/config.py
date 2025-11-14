from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Base(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    base_url: str = Field(
        validation_alias="BASE_URL", default="http://localhost:3000"
    )  # points to the frontend. this could be a different domain based on who the caller is
    env: Literal["development", "production"] = Field(
        validation_alias="APP_ENV", default="development"
    )


class DatabaseSettings(Base):
    database_url: str = Field(validation_alias="DATABASE_URL")


class EmailSettings(Base):
    resend_api_key: str = Field(validation_alias="RESEND_API_KEY")
    from_email: str = "Millennicare<no-reply@millennicare.com>"
    templates_dir: str = "templates/emails"


class StorageSettings(Base):
    cloudflare_account_id: str = Field(validation_alias="CLOUDFLARE_ACCOUNT_ID")
    cloudflare_secret_access_key: str = Field(
        validation_alias="CLOUDFLARE_SECRET_ACCESS_KEY"
    )
    cloudflare_access_key_id: str = Field(validation_alias="CLOUDFLARE_ACCESS_KEY_ID")
    cloudflare_bucket_name: str = Field(validation_alias="CLOUDFLARE_BUCKET_NAME")


class MapsSettings(Base):
    google_maps_api_key: str = Field(validation_alias="GOOGLE_MAPS_API_KEY")


class JWTSettings(Base):
    secret_key: str = Field(validation_alias="SECRET_KEY")


class GoogleOAuthSettings(Base):
    google_client_id: str = Field(validation_alias="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(validation_alias="GOOGLE_CLIENT_SECRET")
    google_redirect_url: str = Field(validation_alias="GOOGLE_REDIRECT_URL")


class CacheSettings(Base):
    redis_host: str = Field(validation_alias="REDIS_HOST", default="localhost")
    redis_port: int = Field(validation_alias="REDIS_PORT", default=6379)


base_settings = Base()
database_settings = DatabaseSettings()
email_settings = EmailSettings()
storage_settings = StorageSettings()
maps_settings = MapsSettings()
jwt_settings = JWTSettings()
google_oauth_settings = GoogleOAuthSettings()
cache_settings = CacheSettings()
