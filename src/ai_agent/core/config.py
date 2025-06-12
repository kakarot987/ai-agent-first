from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI Configuration
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-3.5-turbo", alias="OPENAI_MODEL")
    openai_max_tokens: int = Field(default=150, alias="OPENAI_MAX_TOKENS")
    openai_temperature: float = Field(default=0.7, alias="OPENAI_TEMPERATURE")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")
    # Agent Configuration
    agent_name: str = Field(default="AI Assistant", alias="AGENT_NAME")
    agent_personality: str = Field(default="friendly",
                                   alias="AGENT_PERSONALITY")
    conversation_history_limit: int = Field(default=20,
                                            alias="CONVERSATION_HISTORY_LIMIT")

    # Logging
    log_level: str = Field("INFO", alias="LOG_LEVEL")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "populate_by_name": True  # ← the fix
    }
