from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables or .env."""

    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    openai_max_tokens: int = Field(default=300, gt=0, alias="OPENAI_MAX_TOKENS")
    openai_temperature: float = Field(default=0.7, ge=0, le=2, alias="OPENAI_TEMPERATURE")
    agent_name: str = Field(default="AI Assistant", alias="AGENT_NAME")
    agent_personality: str = Field(default="friendly", alias="AGENT_PERSONALITY")
    conversation_history_limit: int = Field(
        default=20, gt=0, alias="CONVERSATION_HISTORY_LIMIT"
    )
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", populate_by_name=True,
        extra="ignore",
    )
