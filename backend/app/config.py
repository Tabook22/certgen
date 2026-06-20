from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Certificate Generator"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./app.db"
    cors_origins: list[str] = ["http://localhost:5173"]
    max_upload_size_bytes: int = 10 * 1024 * 1024
    storage_root: Path = Path("storage")

    model_config = SettingsConfigDict(env_file=".env", env_prefix="CERTGEN_")

    @property
    def template_storage_path(self) -> Path:
        return self.storage_root / "templates"

    @property
    def import_storage_path(self) -> Path:
        return self.storage_root / "imports"

    @property
    def generated_storage_path(self) -> Path:
        return self.storage_root / "generated"

    @property
    def zip_storage_path(self) -> Path:
        return self.storage_root / "zips"


@lru_cache
def get_settings() -> Settings:
    return Settings()
