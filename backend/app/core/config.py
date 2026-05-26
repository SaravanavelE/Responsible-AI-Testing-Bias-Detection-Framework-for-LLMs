from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "ULockAI Shield"
    app_env: str = "development"
    secret_key: str = "dev-secret-change-in-production-min-32-chars"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    database_url: str = "postgresql+asyncpg://ulockai:ulockai_secret@localhost:5432/ulockai_shield"
    database_url_sync: str = "postgresql://ulockai:ulockai_secret@localhost:5432/ulockai_shield"

    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    s3_endpoint: str = "http://localhost:9000"
    s3_access_key: str = "ulockai_minio"
    s3_secret_key: str = "ulockai_minio_secret"
    s3_bucket: str = "ulockai-reports"
    s3_region: str = "us-east-1"
    s3_use_ssl: bool = False

    encryption_key: str = "dev-fernet-key-replace-in-production"

    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    rate_limit_per_minute: int = 120

    dynamic_probe_provider: str = "openai"
    dynamic_probe_model: str = "gpt-4o-mini"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
