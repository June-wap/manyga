import argparse
import os
import sys
import uuid

from pydantic import ValidationError
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from apps.desktop.supervisor import Supervisor
from apps.desktop.window import MainWindow
from core.config import PROJECT_ROOT, Settings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--connect-backend", action="store_true")
    parser.add_argument("--connect-runtime", action="store_true")
    args = parser.parse_args()
    try:
        settings = Settings()
    except (ValidationError, ValueError):
        print("Invalid LGS configuration. Check .env and LGS_* variables.", file=sys.stderr)
        return 2
    app = QApplication(sys.argv[:1])
    app.setApplicationName("LiveGame Studio")
    supervisor = Supervisor(
        settings, own_backend=not args.connect_backend, own_runtime=not args.connect_runtime
    )
    window = MainWindow(settings, supervisor=supervisor)
    control_directory = PROJECT_ROOT / "runtime"
    control_directory.mkdir(exist_ok=True)
    control = control_directory / f"desktop-{os.getpid()}-{uuid.uuid4().hex}.stop"
    marker = control.with_suffix(".owner")
    marker.write_text("LiveGame Studio desktop control marker", encoding="utf-8")
    stop_timer = QTimer(window)
    stop_timer.setInterval(400)
    stop_timer.timeout.connect(lambda: window.close() if control.exists() else None)
    stop_timer.start()
    window.show()
    window.start()
    try:
        return app.exec()
    finally:
        marker.unlink(missing_ok=True)
        control.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
