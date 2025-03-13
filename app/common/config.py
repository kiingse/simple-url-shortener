import os

from pydantic import AnyHttpUrl, PostgresDsn, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    # APP
    PROJECT_NAME: str
    VERSION: str = "0.0.1"
    SERVER_HOST: AnyHttpUrl
    API_PREFIX: str = "api/v1"

    SHORT_CODE_LENGTH: int = 8

    # DATABASE
    DATABASE_URI: PostgresDsn
    ASYNC_DB_DRIVER: str = "postgresql+asyncpg"

    @property
    def ASYNC_DATABASE_URI(self):
        path = self.DATABASE_URI.path
        if path is None:
            raise ValidationError("Improper DATABASE_URI configuration, missing path")
        path = path.lstrip("/")

        return self.DATABASE_URI.build(
            scheme=self.ASYNC_DB_DRIVER, path=path, **self.DATABASE_URI.hosts()[0]
        )

    # LOGGING
    LOGGING_CONF_FILE: str = "logging.conf"

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=os.environ.get("ENV", ".env"),
    )


config = Config()
