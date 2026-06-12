from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: Literal["local", "test", "production"] = "local"
    database_url: PostgresDsn | str = "sqlite+aiosqlite:///./leadhunter.db"
    redis_url: RedisDsn | str = "redis://redis:6379/0"
    jwt_secret: str = Field(default="change-me-in-production", min_length=16)
    csrf_token: str = Field(default="local-csrf-token", min_length=8)
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60
    cors_origins: list[str] = ["http://localhost:5173"]
    cors_origin_regex: str | None = r"chrome-extension://.*"
    openai_api_key: str | None = None
    search_provider: Literal["brave", "serpapi"] = "brave"
    brave_search_api_key: str | None = None
    serpapi_api_key: str | None = None
    search_provider_api_key: str | None = None
    github_token: str | None = None
    reddit_client_id: str | None = None
    reddit_client_secret: str | None = None
    max_results_per_query: int = Field(default=10, ge=1, le=50)
    rate_limit_default: str = "120/minute"

    @property
    def active_search_api_key(self) -> str | None:
        if self.search_provider == "brave":
            return self.brave_search_api_key or self.search_provider_api_key
        if self.search_provider == "serpapi":
            return self.serpapi_api_key or self.search_provider_api_key
        return self.search_provider_api_key

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
