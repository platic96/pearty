from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./investpulse.db"
    UPBIT_API_BASE_URL: str = "https://api.upbit.com/v1"
    DISCORD_WEBHOOK_URL: str = ""
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
