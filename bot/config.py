"""Configuration loading from environment variables."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings


class BotSettings(BaseSettings):
    """Bot configuration settings."""
    
    # Telegram
    bot_token: str = ""
    
    # LMS API
    lms_api_base_url: str = "http://localhost:42002"
    lms_api_key: str = ""
    
    # LLM API
    llm_api_key: str = ""
    llm_api_base_url: str = ""
    llm_api_model: str = "coder-model"
    
    class Config:
        env_file = str(Path(__file__).parent.parent / ".env.bot.secret")
        env_file_encoding = "utf-8"


# Global settings instance
_settings: BotSettings | None = None


def get_settings() -> BotSettings:
    """Get the bot settings, loading them if necessary."""
    global _settings
    if _settings is None:
        _settings = BotSettings()
    return _settings
