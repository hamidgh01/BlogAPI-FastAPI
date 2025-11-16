""" basic settings and configurations of project """

from pathlib import Path

from pydantic import computed_field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_core import MultiHostUrl


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_ignore_empty=True,
        extra="ignore",
    )

    # app_name: str = "Blog API - FastAPI"
    # admin_email: str

    # Postgres:
    PG_SERVER: str
    PG_PORT: int = 5432
    PG_DB: str
    PG_USER: str
    PG_PASSWORD: str

    @computed_field
    @property
    def SQLALCHEMY_DB_URL(self) -> PostgresDsn:
        url = MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.PG_USER,
            password=self.PG_PASSWORD,
            host=self.PG_SERVER,
            port=self.PG_PORT,
            path=self.PG_DB
        )
        return PostgresDsn(url)

    # Redis:
    REDIS_URL: str
    MAX_CONNECTIONS_PER_PROCESS: int = 100
    TCP_CONNECTION_ESTABLISHMENT_TIMEOUT: int = 3

    # JWT settings:
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 21600  # 15 days (15 * 24 * 60 = 21600)


settings = Settings()
