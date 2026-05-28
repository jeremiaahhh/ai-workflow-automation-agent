from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "AI Workflow Automation Agent"
    log_level: str = "INFO"

    database_url: str = "sqlite:///./agent.db"

    use_mock_ai: bool = True
    ai_provider: Literal["openai", "anthropic"] = "openai"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-6"

    max_steps_per_plan: int = 8
    execution_timeout_seconds: int = 30

    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_mock_mode(self) -> bool:
        if self.use_mock_ai:
            return True
        if self.ai_provider == "openai" and not self.openai_api_key:
            return True
        if self.ai_provider == "anthropic" and not self.anthropic_api_key:
            return True
        return False


@lru_cache
def get_settings() -> Settings:
    return Settings()
