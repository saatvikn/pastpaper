from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    database_url: str
    test_database_url: str | None = None
    storage_dir: Path = ENV_FILE.parent / "data" / "papers"
    max_upload_bytes: int = Field(default=20 * 1024 * 1024, gt=0)
    max_pdf_pages: int = Field(default=100, gt=0)

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")


settings = Settings()
