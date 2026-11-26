"""Real, visible Qt/WebGL acceptance smoke with evidence and bounded timeouts.

Run with .venv/Scripts/python.exe scripts/gui_smoke.py from the workspace.
No GPU switches, sandbox exceptions, remote debugging, or mock renderer.
"""

import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PySide6.QtCore import QProcess, QTimer
from PySide6.QtWidgets import QApplication

from apps.desktop.window import MainWindow
from core.config import Settings


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def main():
    evidence = Path(os.environ.get("LGS_EVIDENCE_DIR", ROOT / "docs/evidence/gd01"))
    evidence.mkdir(parents=True, exist_ok=True)
    data = ROOT / "runtime/gui-smoke"
    ports = [free_port(), free_port()]
    settings = Settings(
        _env_file=None,
        backend_port=ports[0],
        runtime_url=f"http://127.0.0.1:{ports[1]}",
        data_dir=data,
        log_dir=data / "logs",
        db_path=data / "smoke.sqlite3",
    )
    app = QApplication(sys.argv[:1])
    app.setQuitOnLastWindowClosed(False)
    window = MainWindow(settings)
    result = {"status": "FAIL", "checks": {}, "ports": ports, "gpu_flags": "none"}
    stage = 0
    deadline = time.monotonic() + 45
    pids = []
    checks = result["checks"]

    def tick():
        nonlocal stage, deadline
        try:
            if time.monotonic() > deadline:
                raise TimeoutError(f"GUI smoke timeout at stage {stage}")
            if stage == 0 and window.banner.text() == "Connected":
                checks["backend_health"] = "PASS"
                checks["sqlite"] = "PASS" if "PASS" in window.cards["sqlite"].text() else "FAIL"
                window.grab().save(str(evidence / "desktop-dashboard.png"))
                pids.extend(
                    [
                        int(window.supervisor.backend.processId()),
                        int(window.supervisor.runtime.processId()),
                    ]
                )
                listeners = subprocess.run(
                    [
                        "powershell.exe",
                        "-NoProfile",
                        "-Command",
                        f"Get-NetTCPConnection -State Listen -LocalPort {ports[0]} | Select-Object LocalAddress,LocalPort,OwningProcess | ConvertTo-Json -Compress",
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
                binding = json.loads(listeners.stdout)
                assert binding["LocalAddress"] == "127.0.0.1", binding
                result["backend_binding"] = binding
                checks["loopback_binding"] = "PASS"
                window.nav.setCurrentRow(2)
                stage = 1
            elif stage == 1 and window.diagnostic.get("frames", 0) > 6:
                diag = window.diagnostic
                assert diag["state"] == "running" and diag["drawCalls"] > 0
                assert abs(diag["aspect"] - 9 / 16) < 0.0001
                result["embedded_webgl"] = diag
                checks["embedded_webgl"] = "PASS"
                window.grab().save(str(evidence / "desktop-preview.png"))
                result["descendants"] = json.loads(
                    subprocess.run(
                        [
                            "powershell.exe",
                            "-NoProfile",
                            "-Command",
                            f"$allProcesses = @(Get-CimInstance Win32_Process); $ownedIds = @({os.getpid()}); do {{ $newChildren = @($allProcesses | Where-Object {{ $_.ParentProcessId -in $ownedIds -and $_.ProcessId -notin $ownedIds }}); $ownedIds += @($newChildren | ForEach-Object ProcessId) }} while ($newChildren.Count -gt 0); @($allProcesses | Where-Object {{ $_.ProcessId -in $ownedIds -and $_.ProcessId -ne {os.getpid()} -and $_.Name -ne 'powershell.exe' }} | Select-Object ProcessId,Name) | ConvertTo-Json -Compress",
                        ],
                        capture_output=True,
                        text=True,
                        check=True,
                        creationflags=subprocess.CREATE_NO_WINDOW,
                    ).stdout
                )
                window.resize(1100, 760)
                stage = 2
            elif (
                stage == 2
                and window.diagnostic.get("frames", 0) > result["embedded_webgl"]["frames"]
            ):
                assert abs(window.diagnostic["width"] / window.diagnostic["height"] - 9 / 16) < 0.01
                checks["resize_and_animation"] = "PASS"
                # Stop the actual backend via its private control pipe, keep Qt open to see offline.
                window.supervisor.backend.write(b"STOP\n")
                window.supervisor.backend.closeWriteChannel()
                stage = 3
                window.supervisor.deadline = time.monotonic()
            elif stage == 3 and "Unavailable" in window.banner.text():
                checks["backend_unavailable"] = "PASS"
                result["backend_exit_code"] = window.supervisor.backend.exitCode()
                window.nav.setCurrentRow(0)
                window.grab().save(str(evidence / "desktop-offline.png"))
                window.close()
                stage = 4
            elif stage == 4 and window.done:
                assert all(
                    p.state() == QProcess.ProcessState.NotRunning
                    for p in (window.supervisor.backend, window.supervisor.runtime)
                )
                assert result["backend_exit_code"] == 0
                checks["owned_shutdown"] = "PASS"
                result["owned_pids"] = pids
                result["status"] = "PASS"
                timer.stop()
                QTimer.singleShot(500, app.quit)
        except Exception as exc:  # noqa: BLE001 -- record any acceptance failure and close owned children
            result["error"] = str(exc)
            timer.stop()
            window.close()
            QTimer.singleShot(7000, app.quit)

    timer = QTimer()
    timer.setInterval(200)
    timer.timeout.connect(tick)
    window.show()
    window.start()
    timer.start()
    app.exec()
    (evidence / "embedded-smoke.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
