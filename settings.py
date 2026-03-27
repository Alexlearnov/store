from pathlib import Path

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    db_url_raw: AnyUrl = Field(
        alias="DB_URL", description="Строка для подключения к ДБ."
    )
    model_config = SettingsConfigDict(
        env_file=_BASE_DIR / ".env", env_file_encoding="utf-8"
    )

    @property
    def db_url(self) -> str:
        return str(self.db_url_raw)


CONFIG = Settings()
