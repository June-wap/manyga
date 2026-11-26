import sqlite3
import subprocess
import sys
from contextlib import closing

from core.config import PROJECT_ROOT


def test_real_unicode_cwd_data_isolation_and_restart(managed_backend, tmp_path):
    data_a, data_b = tmp_path / "Dữ liệu A", tmp_path / "Dữ liệu B"
    cwd = tmp_path / "Thư mục có dấu cách và Unicode"
    with managed_backend(data_root=data_a, cwd=cwd) as first:
        assert first.health["data"]["status"] == "running"
        with closing(sqlite3.connect(first.db_path)) as db, db:
            db.execute("INSERT INTO foundation_smoke VALUES (42, 'only data A')")
    assert first.exit_code == 0
    with (
        managed_backend(data_root=data_b, cwd=cwd) as other,
        closing(sqlite3.connect(other.db_path)) as db,
    ):
        assert db.execute("SELECT value FROM foundation_smoke WHERE id=42").fetchone() is None
    assert other.exit_code == 0
    with (
        managed_backend(data_root=data_a, cwd=cwd) as restarted,
        closing(sqlite3.connect(restarted.db_path)) as db,
    ):
        assert db.execute("SELECT value FROM foundation_smoke WHERE id=42").fetchone() == (
            "only data A",
        )
    assert restarted.exit_code == 0


def test_actual_cli_port_conflict_does_not_stop_owner(managed_backend, tmp_path):
    with managed_backend() as owner:
        env = owner.env.copy()
        env["LGS_DB_PATH"] = str(tmp_path / "conflict-data/smoke.sqlite3")
        env["LGS_LOG_DIR"] = str(tmp_path / "conflict-data/logs")
        conflict = subprocess.run(
            [sys.executable, "-m", "apps.backend"],
            env=env,
            cwd=owner.cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
            timeout=15,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        assert conflict.returncode != 0
        assert owner.process.poll() is None
        assert owner.client.get("/api/v1/health").status_code == 200
    assert owner.exit_code == 0


def test_real_http_security_boundaries(managed_backend):
    with managed_backend(environment="development") as backend:
        client = backend.client
        public = client.get("/api/v1/health")
        assert public.status_code == 200
        assert set(public.json()["data"]) == {"status", "version", "db_smoke_ok", "uptime_s"}
        assert str(backend.data_root) not in public.text
        assert client.get("/api/v1/health", headers={"Host": "evil.example"}).status_code == 400
        denied = client.get("/api/v1/health", headers={"Origin": "https://evil.example"})
        assert denied.status_code == 403
        assert "access-control-allow-origin" not in denied.headers
        assert client.get("/dev/admin-ping").status_code == 401
        assert (
            client.get(
                "/dev/admin-ping", headers={"Authorization": "Bearer rc1-invalid"}
            ).status_code
            == 401
        )
    assert backend.exit_code == 0
    assert "rc1-invalid" not in backend.output


def test_environment_check_without_optional_gpu_tool():
    # Hide only the optional capability in this child shell; do not alter machine policy/PATH.
    code = r"""
function Get-Command {
    [CmdletBinding()] param([string]$Name)
    if ($Name -eq 'nvidia-smi') {
        Write-Output 'RC1_GPU_TOOL_UNAVAILABLE' | Out-Host
        return $null
    }
    Microsoft.PowerShell.Core\Get-Command @PSBoundParameters
}
& '.\scripts\check_environment.ps1'
"""
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", code],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=20,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    assert result.returncode == 0, result.stderr
    assert "RC1_GPU_TOOL_UNAVAILABLE" in result.stdout
    assert "Python 3.11" in result.stdout
