"""Run RC1 checks and retain sanitized test-command output, never application databases/logs.

Does not invoke Antigravity or change permission/execution policies.
"""

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/evidence/gd01/rc1"


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def main():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    assert git("branch", "--show-current") == "integration/gd01"
    assert git("merge-base", "--is-ancestor", "959bb3a", "HEAD") == ""
    files = git(
        "ls-files",
        "core",
        "apps",
        "frontend",
        "scripts",
        "tests",
        "pyproject.toml",
        "requirements.lock",
        ".env.example",
    ).splitlines()
    manifest = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in files}
    (EVIDENCE / "source-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    (EVIDENCE / "source-tree.txt").write_text("\n".join(files) + "\n", encoding="utf-8")
    base_temp = (ROOT / "runtime/rc1-pytest").resolve()
    assert base_temp.is_relative_to(ROOT)
    node = shutil.which("node")
    npm = shutil.which("npm.cmd")
    if not node or not npm:
        raise RuntimeError("RC1 requires the development Node/npm environment")
    npm_cli = Path(npm).parent / "node_modules/npm/bin/npm-cli.js"
    if not npm_cli.exists():
        raise RuntimeError("Cannot resolve npm CLI beside npm.cmd")
    env = os.environ.copy()
    env.update(PYTHONUTF8="1", LGS_EVIDENCE_DIR=str(EVIDENCE), NO_COLOR="1")
    env.pop("FORCE_COLOR", None)
    steps = [
        ("ruff", [sys.executable, "-m", "ruff", "check", "core", "apps", "scripts", "tests"], ROOT),
        (
            "pytest",
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "--basetemp=" + str(base_temp),
                "--junitxml=" + str(ROOT / "runtime/rc1-pytest.xml"),
            ],
            ROOT,
        ),
        ("typecheck", [node, str(npm_cli), "run", "typecheck"], ROOT / "frontend"),
        ("production-build", [node, str(npm_cli), "run", "build"], ROOT / "frontend"),
        ("vitest", [node, str(npm_cli), "test"], ROOT / "frontend"),
        ("playwright", [node, str(npm_cli), "run", "test:e2e"], ROOT / "frontend"),
        ("embedded-and-cleanup", [sys.executable, "scripts/verify_integration.py"], ROOT),
        ("desktop-start-stop", [sys.executable, "scripts/verify_dev_scripts.py"], ROOT),
        ("pip-check", [sys.executable, "-m", "pip", "check"], ROOT),
    ]
    results = []
    for name, command, cwd in steps:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        output = completed.stdout + completed.stderr
        output = re.sub(r"\x1b\[[0-9;]*m", "", output)
        for home in (str(Path.home()), Path.home().as_posix()):
            output = output.replace(home, "<USERPROFILE>")
        (EVIDENCE / f"{name}.txt").write_text(output, encoding="utf-8")
        results.append(
            {
                "check": name,
                "command": command,
                "cwd": str(cwd),
                "exit_code": completed.returncode,
                "status": "PASS" if completed.returncode == 0 else "FAIL",
                "output": f"{name}.txt",
            }
        )
        print(f"{name}: {results[-1]['status']} (exit {completed.returncode})", flush=True)
    tests = ET.parse(ROOT / "runtime/rc1-pytest.xml").getroot()
    suites = list(tests.iter("testsuite"))
    counts = {
        key: sum(int(s.get(key, 0)) for s in suites)
        for key in ("tests", "failures", "errors", "skipped")
    }
    summary = {
        "reviewed_source_commit": git("rev-parse", "HEAD"),
        "baseline": git("rev-parse", "959bb3a"),
        "accepted_GD00": git("rev-parse", "592db85"),
        "branch": git("branch", "--show-current"),
        "python_counts": counts,
        "commands": results,
        "independent_review_status": "BLOCKED — existing Antigravity command-permission denial; not retried",
        "overall_acceptance_status": "PARTIAL",
    }
    for name in ("vitest", "playwright"):
        raw = (EVIDENCE / f"{name}.txt").read_text(encoding="utf-8")
        pattern = r"Tests\s+(\d+) passed" if name == "vitest" else r"(\d+) passed \("
        match = re.search(pattern, raw)
        summary[name + "_passed"] = int(match.group(1)) if match else None
    (EVIDENCE / "commands.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    assert manifest == {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in files
    }
    return 0 if all(result["exit_code"] == 0 for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
