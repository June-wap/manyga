"""Exercise the user-facing PowerShell start/stop flow on isolated loopback ports."""

import json
import os
import socket
import subprocess
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def main():
    env = os.environ.copy()
    port, runtime_port = free_port(), free_port()
    data = ROOT / "runtime/script-smoke"
    data.mkdir(parents=True, exist_ok=True)
    env.update(
        LGS_BACKEND_PORT=str(port),
        LGS_RUNTIME_URL=f"http://127.0.0.1:{runtime_port}",
        LGS_DATA_DIR=str(data),
        LGS_DB_PATH=str(data / "smoke.sqlite3"),
        LGS_LOG_DIR=str(data / "logs"),
    )
    start = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File"]
    result = {"status": "FAIL", "start_dev": "NOT RUN", "stop_dev": "NOT RUN"}
    with (data / "console.log").open("w", encoding="utf-8") as output:
        process = subprocess.Popen(
            start + [str(ROOT / "scripts/start_dev.ps1")],
            cwd=ROOT,
            env=env,
            stdout=output,
            stderr=output,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        try:
            with httpx.Client(timeout=1, trust_env=False) as client:
                deadline = time.monotonic() + 30
                while time.monotonic() < deadline:
                    try:
                        health = client.get(f"http://127.0.0.1:{port}/api/v1/health")
                        runtime = client.get(f"http://127.0.0.1:{runtime_port}")
                        if health.status_code == runtime.status_code == 200:
                            assert health.json()["data"]["db_smoke_ok"] is True
                            result["start_dev"] = "PASS"
                            break
                    except httpx.HTTPError:
                        pass
                    if process.poll() is not None:
                        raise RuntimeError("Desktop script exited before readiness")
                    time.sleep(0.2)
                else:
                    raise TimeoutError("start_dev readiness timeout")
            subprocess.run(
                start + [str(ROOT / "scripts/stop_dev.ps1")],
                cwd=ROOT,
                check=True,
                timeout=15,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            assert process.wait(timeout=20) == 0
            # Inspect listeners directly: Windows connection refusal can exceed HTTP timeout.
            sockets = subprocess.run(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-Command",
                    f"@(Get-NetTCPConnection -State Listen | Where-Object LocalPort -in @({port},{runtime_port}) | Select-Object LocalPort,OwningProcess) | ConvertTo-Json -Compress",
                ],
                check=True,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            listeners = json.loads(sockets.stdout) if sockets.stdout.strip() else []
            assert not listeners, listeners
            result["remaining_listeners"] = listeners
            result.update(status="PASS", stop_dev="PASS", desktop_exit_code=process.returncode)
        finally:
            if process.poll() is None:
                subprocess.run(
                    start + [str(ROOT / "scripts/stop_dev.ps1")],
                    cwd=ROOT,
                    check=False,
                    timeout=15,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
                process.wait(timeout=20)
    (ROOT / "docs/evidence/gd01/dev-script-smoke.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
