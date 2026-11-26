import os
import socket
import subprocess
import sys
import time
from contextlib import contextmanager
from types import SimpleNamespace

import httpx
import pytest

from core.config import PROJECT_ROOT, Settings


@pytest.fixture
def settings(tmp_path):
    return Settings(
        _env_file=None,
        environment="test",
        data_dir=tmp_path / "data",
        log_dir=tmp_path / "logs",
        db_path=tmp_path / "smoke.sqlite3",
    )


@pytest.fixture
def managed_backend(tmp_path):
    """Real process/HTTP lifecycle, isolated paths, safe owned-tree cleanup on test failure."""

    @contextmanager
    def launch(*, data_root=None, cwd=None, script=None, environment="test", port=None):
        data_root = data_root or tmp_path / "Dữ liệu RC1"
        cwd = cwd or tmp_path / "Thư mục làm việc RC1"
        cwd.mkdir(parents=True, exist_ok=True)
        if port is None:
            with socket.socket() as sock:
                sock.bind(("127.0.0.1", 0))
                port = sock.getsockname()[1]
        env = {key: value for key, value in os.environ.items() if not key.startswith("LGS_")}
        env.update(
            PYTHONPATH=str(PROJECT_ROOT),
            PYTHONUTF8="1",
            LGS_ENVIRONMENT=environment,
            LGS_BACKEND_HOST="127.0.0.1",
            LGS_BACKEND_PORT=str(port),
            LGS_RUNTIME_URL="http://127.0.0.1:5173",
            LGS_DATA_DIR=str(data_root),
            LGS_DB_PATH=str(data_root / "database/smoke.sqlite3"),
            LGS_LOG_DIR=str(data_root / "logs"),
            LGS_CONFIG_DIR=str(data_root / "config"),
            LGS_ASSET_DIR=str(data_root / "assets"),
            LGS_CACHE_DIR=str(data_root / "cache"),
        )
        args = [sys.executable, str(script)] if script else [sys.executable, "-m", "apps.backend"]
        output = (cwd / "backend-test-output.txt").open("w+", encoding="utf-8")
        process = subprocess.Popen(
            [*args, "--supervised"],
            cwd=cwd,
            env=env,
            stdin=subprocess.PIPE,
            stdout=output,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        state = SimpleNamespace(
            process=process,
            port=port,
            data_root=data_root,
            db_path=data_root / "database/smoke.sqlite3",
            output="",
            exit_code=None,
            env=env,
            cwd=cwd,
        )
        try:
            with httpx.Client(
                base_url=f"http://127.0.0.1:{port}", trust_env=False, timeout=0.5
            ) as client:
                state.client = client
                deadline = time.monotonic() + 20
                while time.monotonic() < deadline:
                    try:
                        response = client.get("/api/v1/health")
                        if response.status_code == 200 and response.json()["data"]["db_smoke_ok"]:
                            state.health = response.json()
                            break
                    except httpx.HTTPError:
                        pass
                    if process.poll() is not None:
                        raise RuntimeError("Backend exited before readiness")
                    time.sleep(0.05)
                else:
                    raise TimeoutError("Backend readiness timed out")
                yield state
        finally:
            try:
                process.communicate(input="STOP\n" if process.poll() is None else None, timeout=10)
            except subprocess.TimeoutExpired:
                subprocess.run(
                    ["taskkill.exe", "/PID", str(process.pid), "/T", "/F"],
                    check=False,
                    capture_output=True,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
                process.communicate(timeout=5)
                raise AssertionError("Owned backend failed graceful shutdown") from None
            finally:
                state.exit_code = process.returncode
                output.flush()
                output.seek(0)
                state.output = output.read()
                output.close()

    return launch
