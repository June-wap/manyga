import json
import logging
import sqlite3
from contextlib import closing

import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from pydantic import BaseModel, ValidationError

from apps.backend.main import create_app, require_admin
from core.config import PROJECT_ROOT, Settings
from core.logging import close_logging, configure_logging
from core.security import SessionCredentials
from core.sqlite_smoke import connect, run_smoke


def test_settings_defaults_and_relative_paths(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    settings = Settings(_env_file=None)
    assert settings.backend_host == "127.0.0.1"
    assert settings.data_dir == PROJECT_ROOT / "data"
    assert settings.db_path == PROJECT_ROOT / "data/smoke.sqlite3"


@pytest.mark.parametrize(
    "override",
    [
        {"backend_host": "0.0.0.0"},
        {"backend_host": "192.168.0.1"},
        {"backend_port": 0},
        {"backend_port": 65536},
        {"environment": "production"},
        {"runtime_url": "https://evil.example:5173"},
        {"runtime_url": "http://127.0.0.1:5173/?token=x"},
        {"runtime_url": "http://admin:secret@127.0.0.1:5173"},
        {"runtime_url": "http://127.0.0.1:8765"},
        {"readiness_timeout_s": 0},
    ],
)
def test_invalid_settings(override):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, **override)


def test_environment_and_dotenv(monkeypatch, tmp_path):
    env = tmp_path / ".env"
    env.write_text("LGS_BACKEND_PORT=8800\nLGS_ENVIRONMENT=test\n", encoding="utf-8")
    monkeypatch.setenv("LGS_BACKEND_PORT", "8801")
    assert Settings(_env_file=env).backend_port == 8801
    assert Settings(_env_file=env).environment == "test"


def test_redaction_and_utf8(settings):
    logger = configure_logging(settings.log_dir, ["fake-runtime-credential"])
    try:
        logger.info(
            {
                "hello": "Tiếng Việt — Tu Tiên",
                "nested": {
                    "token": "fake-token",
                    "secret": "fake-secret",
                    "password": "fake-password",
                    "authorization": "fake-auth",
                    "cookie": "fake-cookie",
                    "api_key": "fake-key",
                },
            }
        )
        logger.warning("Bearer fake-runtime-credential token=fake-token password=fake-password")
        try:
            raise RuntimeError("fake-runtime-credential api_key=fake-key")
        except RuntimeError:
            logger.exception("Exception smoke")
    finally:
        close_logging()
    raw = (settings.log_dir / "studio.jsonl").read_text(encoding="utf-8")
    assert "Tiếng Việt" in raw
    for secret in [
        "fake-token",
        "fake-secret",
        "fake-password",
        "fake-auth",
        "fake-cookie",
        "fake-key",
        "fake-runtime-credential",
    ]:
        assert secret not in raw
    entries = [json.loads(line) for line in raw.splitlines()]
    assert all({"timestamp", "level", "module", "message"} <= e.keys() for e in entries)
    assert "Traceback" in entries[-1]["exception"]


def test_rotating_file(settings):
    logger = configure_logging(settings.log_dir)
    file = logger.handlers[0]
    file.maxBytes = 200
    for _ in range(10):
        logger.info("Rotation smoke — Tiếng Việt")
    close_logging()
    assert (settings.log_dir / "studio.jsonl.1").exists()


def test_sqlite_real_commit_rollback_fk_restart(settings):
    result = run_smoke(settings.db_path)
    assert result["wal"] and result["persistent"] and result["foreign_keys"]
    assert result["busy_timeout_ms"] == 5000
    with closing(connect(settings.db_path)) as db:
        with db:
            db.execute("INSERT INTO foundation_smoke VALUES (2, 'committed')")
        with pytest.raises(sqlite3.IntegrityError), db:
            db.execute("UPDATE foundation_smoke SET value='should rollback' WHERE id=2")
            db.execute("INSERT INTO foundation_smoke_child VALUES (999)")
    with closing(connect(settings.db_path)) as db:
        assert db.execute("SELECT value FROM foundation_smoke WHERE id=2").fetchone() == (
            "committed",
        )
    assert run_smoke(settings.db_path)["persistent"]


def test_health_and_lifecycle(settings):
    app = create_app(settings)
    assert not app.state.core.running
    with TestClient(app, base_url="http://127.0.0.1") as client:
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        body = response.json()
        assert body["ok"] is True
        assert set(body["data"]) == {"status", "version", "db_smoke_ok", "uptime_s"}
        assert body["data"]["db_smoke_ok"] is True
        assert app.state.core.running
        for secret in [
            str(settings.db_path),
            str(settings.log_dir),
            app.state.core.credentials.admin.get_secret_value(),
            app.state.core.credentials.renderer.get_secret_value(),
        ]:
            assert secret not in response.text
    assert not app.state.core.running
    assert not logging.getLogger("lgs").handlers
    raw = (settings.log_dir / "studio.jsonl").read_text(encoding="utf-8")
    assert "Application started" in raw and "Application shutdown" in raw


def test_startup_failure_closes_log_resources(settings):
    settings.db_path.mkdir()
    app = create_app(settings)
    with pytest.raises(sqlite3.OperationalError), TestClient(app, base_url="http://127.0.0.1"):
        pass
    assert not app.state.core.running
    assert not logging.getLogger("lgs").handlers


@pytest.mark.parametrize("host", ["evil.example", "127.0.0.1.evil.example", "192.168.1.1"])
def test_trusted_host(settings, host):
    with TestClient(create_app(settings), base_url="http://127.0.0.1") as client:
        assert client.get("/api/v1/health", headers={"host": host}).status_code == 400


@pytest.mark.parametrize("origin", ["https://evil.example", "null", "http://localhost:9999"])
def test_origin_rejection(settings, origin):
    with TestClient(create_app(settings), base_url="http://127.0.0.1") as client:
        response = client.get("/api/v1/health", headers={"Origin": origin})
        assert response.status_code == 403
        assert "access-control-allow-origin" not in response.headers


def test_allowed_origin_and_preflight(settings):
    with TestClient(create_app(settings), base_url="http://localhost") as client:
        origin = settings.runtime_url
        response = client.get("/api/v1/health", headers={"origin": origin})
        assert response.headers["access-control-allow-origin"] == origin
        response = client.options(
            "/api/v1/health", headers={"origin": origin, "access-control-request-method": "GET"}
        )
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] != "*"


def test_admin_renderer_boundary(settings):
    settings.environment = "development"
    app = create_app(settings)
    with TestClient(app, base_url="http://127.0.0.1") as client:
        for value in [
            None,
            "invalid",
            app.state.core.credentials.renderer.get_secret_value(),
            "非ASCII",
        ]:
            # HTTP headers themselves are ASCII; the comparator also handles non-ASCII input safely.
            if value == "非ASCII":
                assert not app.state.core.credentials.permits_admin(value)
                continue
            headers = {} if value is None else {"authorization": "Bearer " + value}
            assert client.get("/dev/admin-ping", headers=headers).status_code == 401
        response = client.get(
            "/dev/admin-ping",
            headers={
                "authorization": "Bearer " + app.state.core.credentials.admin.get_secret_value()
            },
        )
        assert response.status_code == 200
    assert SessionCredentials().admin != SessionCredentials().admin
    assert "SecretStr" not in repr(app.state.core.credentials)


def test_dev_endpoint_absent_in_test(settings):
    with TestClient(create_app(settings), base_url="http://127.0.0.1") as client:
        assert client.get("/dev/admin-ping").status_code == 404


def test_safe_errors_and_validation(settings):
    app = create_app(settings)

    @app.get("/test-exception")
    def crash():
        raise RuntimeError("C:/private/path token=fake-secret")

    class Input(BaseModel):
        count: int

    @app.post("/test-input", dependencies=[Depends(require_admin)])
    def input_route(data: Input):
        return data

    with TestClient(app, base_url="http://127.0.0.1", raise_server_exceptions=False) as client:
        response = client.get("/test-exception")
        assert response.status_code == 500
        assert "private" not in response.text and "fake-secret" not in response.text
        token = app.state.core.credentials.admin.get_secret_value()
        response = client.post(
            "/test-input",
            json={"count": "password=fake-secret"},
            headers={"authorization": "Bearer " + token},
        )
        assert response.status_code == 422
        assert "fake-secret" not in response.text
    assert "fake-secret" not in (settings.log_dir / "studio.jsonl").read_text(encoding="utf-8")
