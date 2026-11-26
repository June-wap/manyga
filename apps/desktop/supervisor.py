"""Nonblocking Qt process ownership and HTTP readiness. No broad process termination."""

import json
import shutil
import socket
import sys
import time
from urllib.parse import urlsplit

from PySide6.QtCore import QObject, QProcess, QProcessEnvironment, QTimer, QUrl, Signal
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest

from core.config import PROJECT_ROOT, Settings


def port_free(port: int) -> bool:
    try:
        with socket.socket() as sock:
            if sys.platform == "win32":
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            sock.bind(("127.0.0.1", port))
        return True
    except OSError:
        return False


class Supervisor(QObject):
    backend_status = Signal(str, object)
    runtime_ready = Signal()
    runtime_error = Signal(str)
    stopped = Signal()

    def __init__(self, settings: Settings, *, own_backend=True, own_runtime=True, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.own_backend, self.own_runtime = own_backend, own_runtime
        self.backend = QProcess(self)
        self.runtime = QProcess(self)
        self.net = QNetworkAccessManager(self)
        self.poller = QTimer(self)
        self.poller.setInterval(700)
        self.poller.timeout.connect(self.poll)
        self.kill_timer = QTimer(self)
        self.kill_timer.setSingleShot(True)
        self.kill_timer.timeout.connect(self.force_owned_stop)
        self.closing = False
        self.pending = set()
        self.replies = set()
        self.stop_helpers = []
        self.runtime_loaded = False
        self.backend_conflict = False
        self.runtime_conflict = False
        for process in (self.backend, self.runtime):
            process.finished.connect(self.check_stopped)
            process.setWorkingDirectory(str(PROJECT_ROOT))
            # Drain child output, but never reflect arbitrary process output into UI/logs.
            process.readyReadStandardOutput.connect(process.readAllStandardOutput)
            process.readyReadStandardError.connect(process.readAllStandardError)
            process.errorOccurred.connect(self.process_error)

    def process_error(self, error):
        if self.closing:
            self.check_stopped()
        else:
            self.backend_status.emit("Backend Unavailable — process error; kiểm tra môi trường", {})

    def start(self):
        self.deadline = time.monotonic() + self.settings.readiness_timeout_s
        self.backend_status.emit("Loading — chờ backend", {})
        if self.own_backend:
            if not port_free(self.settings.backend_port):
                self.backend_conflict = True
                self.backend_status.emit("Backend Unavailable — port conflict", {})
            else:
                env = QProcessEnvironment.systemEnvironment()
                for key, value in {
                    "LGS_BACKEND_PORT": str(self.settings.backend_port),
                    "LGS_ENVIRONMENT": self.settings.environment,
                    "LGS_BACKEND_HOST": self.settings.backend_host,
                    "LGS_RUNTIME_URL": self.settings.runtime_url,
                    "LGS_DB_PATH": str(self.settings.db_path),
                    "LGS_DATA_DIR": str(self.settings.data_dir),
                    "LGS_LOG_DIR": str(self.settings.log_dir),
                }.items():
                    env.insert(key, value)
                self.backend.setProcessEnvironment(env)
                self.backend.start(sys.executable, ["-m", "apps.backend", "--supervised"])
        if self.own_runtime:
            port = urlsplit(self.settings.runtime_url).port
            vite = PROJECT_ROOT / "frontend/node_modules/vite/bin/vite.js"
            node = shutil.which("node")
            if not port_free(port):
                self.runtime_conflict = True
                self.runtime_error.emit(
                    "Runtime port conflict. Đóng preview cũ hoặc đổi LGS_RUNTIME_URL."
                )
            elif not node or not vite.exists():
                self.runtime_conflict = True
                self.runtime_error.emit("Runtime chưa được cài đặt. Chạy scripts/setup_dev.ps1.")
            else:
                self.runtime.setWorkingDirectory(str(PROJECT_ROOT / "frontend"))
                self.runtime.start(
                    node, [str(vite), "--host", "127.0.0.1", "--port", str(port), "--strictPort"]
                )
        self.poller.start()
        self.poll()

    def poll(self):
        if self.closing:
            return
        if not self.backend_conflict:
            self.request("backend", self.settings.backend_url + "/api/v1/health")
        if not self.runtime_loaded and not self.runtime_conflict:
            self.request("runtime", self.settings.runtime_url)

    def request(self, kind, url):
        if kind in self.pending:
            return
        self.pending.add(kind)
        request = QNetworkRequest(QUrl(url))
        request.setTransferTimeout(1200)
        reply = self.net.get(request)
        self.replies.add(reply)

        def finished():
            self.replies.discard(reply)
            self.pending.discard(kind)
            code = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
            raw = bytes(reply.readAll())
            reply.deleteLater()
            if self.closing:
                return
            if kind == "runtime":
                if code == 200:
                    self.runtime_loaded = True
                    self.runtime_ready.emit()
                elif time.monotonic() > self.deadline:
                    self.runtime_error.emit("Runtime Unavailable — readiness timeout; tự thử lại")
                return
            try:
                payload = json.loads(raw)
                data = payload["data"]
                if code != 200 or payload.get("ok") is not True or data["status"] != "running":
                    raise ValueError()
                self.backend_status.emit("Connected", data)
            except (ValueError, KeyError, TypeError):
                state = (
                    "Backend Unavailable — tự thử lại sau 0.7s"
                    if time.monotonic() > self.deadline
                    else "Loading — chờ backend"
                )
                self.backend_status.emit(state, {})

        reply.finished.connect(finished)

    def stop(self):
        if self.closing:
            return
        self.closing = True
        self.poller.stop()
        for reply in list(self.replies):
            reply.abort()
        if self.backend.state() != QProcess.ProcessState.NotRunning:
            self.backend.write(b"STOP\n")
            self.backend.closeWriteChannel()
        # Vite owns no child node process: direct node entrypoint, never npm/cmd wrapper.
        if self.runtime.state() != QProcess.ProcessState.NotRunning:
            self.runtime.terminate()
        self.kill_timer.start(5000)
        self.check_stopped()

    def force_owned_stop(self):
        for process in (self.backend, self.runtime):
            if process.state() != QProcess.ProcessState.NotRunning:
                if sys.platform == "win32":
                    # The venv launcher may own a real Python grandchild. Target only this
                    # still-running QProcess tree, never an executable name or a stored PID.
                    helper = QProcess(self)
                    helper.finished.connect(self.check_stopped)
                    self.stop_helpers.append(helper)
                    helper.start("taskkill.exe", ["/PID", str(process.processId()), "/T", "/F"])
                else:
                    process.kill()

    def check_stopped(self, *args):
        if self.closing and all(
            p.state() == QProcess.ProcessState.NotRunning
            for p in (self.backend, self.runtime, *self.stop_helpers)
        ):
            self.kill_timer.stop()
            self.stopped.emit()
