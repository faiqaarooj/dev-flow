from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "DevFlow AI Backend"
    openai_api_key: str | None = None
    gemini_api_key: str | None = None
    app_id: str | None = None
    app_secret: str | None = None
    dnotifier_app_id: str | None = None
    dnotifier_app_secret: str | None = None
    ai_provider: str = "gemini"
    database_path: str = "./devflow.db"
    github_api_base_url: str = "https://api.github.com"
    bandit_timeout_seconds: int = 60
    max_repo_files: int = 200
    max_repo_bytes: int = 5_000_000
    max_file_bytes: int = 250_000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
