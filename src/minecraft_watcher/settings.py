from functools import cache

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    log_level: str = "ERROR"
    host: str = "localhost"
    port: int = 25565
    timeout_s: int = 600
    kill_webhook: str = Field(default=...)

    class Config:
        env_file = ".env"


@cache
def get_settings():
    return Settings()
