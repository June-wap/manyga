import json
import subprocess
import sys

from PySide6.QtCore import QProcess

from apps.desktop.supervisor import Supervisor


def test_forced_shutdown_cleans_owned_descendants(qtbot, settings, tmp_path):
    """Real unresponsive Python worker and grandchild; exact owned-tree fallback after timeout."""
    supervisor = Supervisor(settings, own_runtime=False)
    pid_file = tmp_path / "worker-pid.txt"
    code = (
        "import subprocess,sys,time; from pathlib import Path; "
        "child=subprocess.Popen([sys.executable,'-c','import time; time.sleep(90)']); "
        f"Path({str(pid_file)!r}).write_text(str(child.pid)); time.sleep(90)"
    )
    supervisor.backend.start(sys.executable, ["-c", code])
    qtbot.waitUntil(pid_file.exists, timeout=10000)
    child_pid = int(pid_file.read_text())
    try:
        with qtbot.waitSignal(supervisor.stopped, timeout=12000):
            supervisor.stop()
        assert supervisor.backend.state() == QProcess.ProcessState.NotRunning
        assert supervisor.stop_helpers and supervisor.stop_helpers[0].exitCode() == 0
        process = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-Command",
                f"@(Get-CimInstance Win32_Process | Where-Object ProcessId -eq {child_pid} | Select-Object ProcessId) | ConvertTo-Json -Compress",
            ],
            capture_output=True,
            text=True,
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        assert not (json.loads(process.stdout) if process.stdout.strip() else [])
    finally:
        if supervisor.backend.state() != QProcess.ProcessState.NotRunning:
            supervisor.force_owned_stop()
            qtbot.waitUntil(
                lambda: supervisor.backend.state() == QProcess.ProcessState.NotRunning,
                timeout=10000,
            )
