from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    BOT_TOKEN: str = ""
    BOT_USERNAME: str = "GameverseStrategyBot"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    DATABASE_URL: str = "sqlite+aiosqlite:///./gameverse.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_ENABLED: bool = False

    ADMIN_API_KEY: str = "adminkey_super_secret_gameverse_2026"
    ADMIN_TELEGRAM_IDS: Union[List[int], str] = []

    RESOURCE_TICK_SECONDS: int = 60
    BASE_GOLD_PRODUCTION: int = 50
    BASE_WOOD_PRODUCTION: int = 40
    BASE_IRON_PRODUCTION: int = 30
    BASE_FOOD_PRODUCTION: int = 60
    BASE_STORAGE_CAPACITY: int = 5000

    @field_validator("ADMIN_TELEGRAM_IDS", mode="before")
    @classmethod
    def parse_admin_ids(cls, v: Union[str, List[int]]) -> List[int]:
        if isinstance(v, str):
            if not v.strip():
                return []
            return [int(x.strip()) for x in v.split(",") if x.strip().isdigit()]
        return v or []

    @property
    def is_sqlite(self) -> bool:
        return "sqlite" in self.DATABASE_URL


settings = Settings()
