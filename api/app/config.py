from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://vocab:vocab_password@localhost:5432/vocab_tg"
    DB_ECHO: bool = False

    DEEPL_API_KEY: str = ""
    DEEPL_FREE_API: bool = True

    TELEGRAM_BOT_TOKEN: str = ""
    MINI_APP_URL: str = ""
    ALLOWED_ORIGINS: str = ""
    CRON_SECRET: str = ""

    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"

    FSRS_DESIRED_RETENTION: float = 0.9
    FSRS_MAXIMUM_INTERVAL: int = 365

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @model_validator(mode="after")
    def normalize_database_url(self) -> "Settings":
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            self.DATABASE_URL = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and "+asyncpg" not in url:
            self.DATABASE_URL = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self

    @property
    def allowed_origins_list(self) -> list[str]:
        if not self.ALLOWED_ORIGINS:
            return []
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]


settings = Settings()
