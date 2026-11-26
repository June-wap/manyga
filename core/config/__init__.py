"""Validated local development configuration."""

import os
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def local_user_root() -> Path:
    """Per-Windows-user writable root; never installation-relative by default."""
    local = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    if not local.is_absolute():
        raise ValueError("LOCALAPPDATA must be an absolute local directory")
    return local / "LiveGameStudio"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="LGS_",
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="forbid",
        hide_input_in_errors=True,
    )
    environment: Literal["development", "test"] = "development"
    backend_host: Literal["127.0.0.1"] = "127.0.0.1"
    backend_port: int = Field(default=8765, ge=1024, le=65535)
    runtime_url: str = "http://127.0.0.1:5173"
    data_dir: Path = Field(default_factory=local_user_root)
    log_dir: Path | None = None
    db_path: Path | None = None
    config_dir: Path | None = None
    asset_dir: Path | None = None
    cache_dir: Path | None = None
    readiness_timeout_s: float = Field(default=20, gt=0, le=120)

    @field_validator("data_dir", "log_dir", "db_path", "config_dir", "asset_dir", "cache_dir")
    @classmethod
    def resolve_path(cls, value: Path | None) -> Path | None:
        if value is None:
            return None
        if str(value).replace("\\", "/").startswith("//"):
            raise ValueError("Network-share application paths are not supported")
        if os.name == "nt":
            import ctypes

            drive = Path(value).anchor or PROJECT_ROOT.anchor
            if ctypes.windll.kernel32.GetDriveTypeW(drive) == 4:
                raise ValueError("Mapped network-drive application paths are not supported")
        return (PROJECT_ROOT / value).resolve() if not value.is_absolute() else value.resolve()

    @field_validator("runtime_url")
    @classmethod
    def local_runtime(cls, value: str) -> str:
        url = urlsplit(value)
        if (
            url.scheme != "http"
            or url.hostname not in {"127.0.0.1", "localhost"}
            or url.username
            or url.password
            or url.query
            or url.fragment
            or url.path not in {"", "/"}
            or not url.port
        ):
            raise ValueError("runtime_url must be an explicit loopback HTTP origin with port")
        return value.rstrip("/")

    @model_validator(mode="after")
    def distinct_ports(self):
        if urlsplit(self.runtime_url).port == self.backend_port:
            raise ValueError("backend and runtime ports must differ")
        return self

    @model_validator(mode="after")
    def writable_layout(self):
        self.log_dir = self.log_dir or self.data_dir / "logs"
        self.db_path = self.db_path or self.data_dir / "database" / "smoke.sqlite3"
        self.config_dir = self.config_dir or self.data_dir / "config"
        self.asset_dir = self.asset_dir or self.data_dir / "assets"
        self.cache_dir = self.cache_dir or self.data_dir / "cache"
        return self

    @property
    def installation_dir(self) -> Path:
        return PROJECT_ROOT

    @property
    def database_dir(self) -> Path:
        return self.db_path.parent

    @property
    def backend_url(self) -> str:
        return f"http://{self.backend_host}:{self.backend_port}"

    @property
    def allowed_origins(self) -> list[str]:
        port = urlsplit(self.runtime_url).port
        return [
            self.backend_url,
            self.runtime_url,
            f"http://localhost:{port}",
            f"http://localhost:{self.backend_port}",
        ]
