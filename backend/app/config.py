from __future__ import annotations

import os
from pathlib import Path
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    app_name: str = "DevFlow AI Backend"
    openai_api_key: str | None = None
    gemini_api_key: str | None = None
    app_id: str | None = None
    app_secret: str | None = None
    dnotifier_app_id: str | None = None
    dnotifier_app_secret: str | None = None
    dnotifier_api_url: str = "https://api.dnotifier.com"
    ai_provider: str = "gemini"
    database_path: str = "./devflow.db"
    github_api_base_url: str = "https://api.github.com"
    bandit_timeout_seconds: int = 60
    max_repo_files: int = 200
    max_repo_bytes: int = 5_000_000
    max_file_bytes: int = 250_000

    @model_validator(mode="after")
    def sync_dnotifier_credentials(self) -> Settings:
        if not self.dnotifier_app_id and self.app_id:
            self.dnotifier_app_id = self.app_id
        if not self.dnotifier_app_secret and self.app_secret:
            self.dnotifier_app_secret = self.app_secret
        return self

    model_config = SettingsConfigDict(
        env_file=(str(ENV_FILE), ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
