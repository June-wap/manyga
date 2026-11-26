"""Run the real GUI smoke in a process, then prove its descendants have exited."""

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    subprocess.run(
        [sys.executable, str(ROOT / "scripts/gui_smoke.py")], cwd=ROOT, check=True, timeout=90
    )
    evidence = (
        Path(os.environ.get("LGS_EVIDENCE_DIR", ROOT / "docs/evidence/gd01"))
        / "embedded-smoke.json"
    )
    result = json.loads(evidence.read_text(encoding="utf-8"))
    owned = [p["ProcessId"] for p in result["descendants"]]
    query = "$trackedIds = @(" + ",".join(map(str, owned)) + "); "
    query += "@(Get-CimInstance Win32_Process | Where-Object ProcessId -in $trackedIds | Select-Object ProcessId,Name) | ConvertTo-Json -Compress"
    processes = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", query],
        check=True,
        capture_output=True,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    survivors = json.loads(processes.stdout) if processes.stdout.strip() else []
    result["process_survivors"] = survivors
    result["checks"]["no_orphan_descendants"] = "PASS" if not survivors else "FAIL"
    if survivors:
        result["status"] = "FAIL"
    evidence.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("Descendant process shutdown:", result["checks"]["no_orphan_descendants"])
    return 0 if not survivors else 1


if __name__ == "__main__":
    raise SystemExit(main())
