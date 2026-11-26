"""Validated local development configuration."""

from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


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
    data_dir: Path = Path("data")
    log_dir: Path = Path("logs")
    db_path: Path = Path("data/smoke.sqlite3")
    readiness_timeout_s: float = Field(default=20, gt=0, le=120)

    @field_validator("data_dir", "log_dir", "db_path")
    @classmethod
    def resolve_path(cls, value: Path) -> Path:
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
