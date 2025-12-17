from pydantic_settings import BaseSettings, SettingsConfigDict
from tortoise.contrib.fastapi import register_tortoise
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # LLM / Tracing (declare them even if not used here)
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    LANGSMITH_TRACING: Optional[bool] = False
    LANGSMITH_API_KEY: Optional[str] = None
    LANGSMITH_PROJECT: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",       # IMPORTANT
        extra="forbid"       # keep strict
    )


Config = Settings()

# Register all tortoise orm models here

MODELS_LIST = ["agent_v1.api.db.models",  # Register models file here
               "aerich.models"
               ]

# TORTOISE_ORM_CONFIG
tortoise_config = {
    "connections": {"default": Config.DATABASE_URL},
    "apps": {
        "models": {
            "models": MODELS_LIST,
            "default_connection": "default",
        },
    },
    "use_tz": True,  # If you want timezone-aware timestamps
    "timezone": "UTC",
}


def init_db(app):
    # register_tortoise(
    #     app,
    #     config=tortoise_config,
    #     # db_url=Config.database_url,
    #     # modules={"models": ["models"]},
    #     generate_schemas=False,  # Use aerich for migrations
    #     add_exception_handlers=True,
    # )
    try:
        register_tortoise(
            app,
            config=tortoise_config,
            generate_schemas=False,  # Use Aerich for migrations
            add_exception_handlers=True
        )
        print('Database connected and models registered')
    except Exception as e:
        print(f"Error initializing database: {e}")
