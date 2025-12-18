from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from tortoise import Tortoise


class Settings(BaseSettings):
    DATABASE_URL: str

    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    LANGSMITH_TRACING: Optional[bool] = False
    LANGSMITH_API_KEY: Optional[str] = None
    LANGSMITH_PROJECT: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        extra="forbid",
    )


Config = Settings()

MODELS_LIST = [
    "agent_v1.api.db.models",
    "aerich.models",
]

tortoise_config = {
    "connections": {
        "default": Config.DATABASE_URL,
    },
    "apps": {
        "models": {
            "models": MODELS_LIST,
            "default_connection": "default",
        },
    },
    "use_tz": True,
    "timezone": "UTC",
}


async def init_db() -> None:
    """
    Explicit, deterministic DB initialization.
    REQUIRED when accessing models during startup.
    """
    await Tortoise.init(config=tortoise_config)
