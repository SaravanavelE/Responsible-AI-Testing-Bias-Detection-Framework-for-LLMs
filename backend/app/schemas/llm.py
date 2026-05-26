from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class LLMConnectionCreate(BaseModel):
    name: str
    provider: str
    api_key: str
    api_base_url: str
    model_name: str
    custom_headers: dict = {}
    response_json_path: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout_seconds: int = 60
    rate_limit_rpm: int = 60
    tags: list[str] = []
    environment: str = "production"
    region: str = "us-east-1"
    is_shadow: bool = False


class LLMConnectionUpdate(BaseModel):
    name: Optional[str] = None
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None
    model_name: Optional[str] = None
    custom_headers: Optional[dict] = None
    response_json_path: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    timeout_seconds: Optional[int] = None
    rate_limit_rpm: Optional[int] = None
    tags: Optional[list[str]] = None
    environment: Optional[str] = None
    region: Optional[str] = None
    is_active: Optional[bool] = None


class LLMConnectionResponse(BaseModel):
    id: UUID
    name: str
    provider: str
    api_base_url: str
    model_name: str
    response_json_path: str
    temperature: float
    max_tokens: int
    timeout_seconds: int
    rate_limit_rpm: int
    tags: list
    environment: str
    region: str
    health_status: str
    last_health_check: Optional[datetime]
    token_usage_total: int
    is_shadow: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ProviderPreset(BaseModel):
    provider: str
    api_base_url: str
    response_json_path: str
    models: list[str]
