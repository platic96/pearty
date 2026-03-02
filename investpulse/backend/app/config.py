from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./investpulse.db"
    UPBIT_API_BASE_URL: str = "https://api.upbit.com/v1"
    DISCORD_WEBHOOK_URL: str = ""
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    # 한국투자증권 OpenAPI
    KIS_APP_KEY: str = ""
    KIS_APP_SECRET: str = ""
    KIS_BASE_URL: str = "https://openapi.koreainvestment.com:9443"
    KIS_IS_PAPER: bool = True  # True=모의투자, False=실전

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
