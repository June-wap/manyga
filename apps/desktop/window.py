import json

from PySide6.QtCore import QTimer, QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from apps.desktop.supervisor import Supervisor
from core.app import VERSION
from core.config import Settings

NAVIGATION = [
    "Dashboard",
    "Game Library",
    "Live Studio",
    "Game Master",
    "Event Scheduler",
    "Gift Mapping",
    "Players",
    "Asset Library",
    "Characters",
    "Maps",
    "Animations",
    "Event Simulator",
    "Analytics",
    "Settings",
]
PHASES = [
    "GD01",
    "GD05",
    "GD18",
    "GD12",
    "GD12",
    "GD06",
    "GD11",
    "GD07",
    "GD09",
    "GD10",
    "GD09",
    "GD04",
    "GD19",
    "GD03",
]

STYLE = """
QWidget { background: #0F1117; color: #F3F4F6; font-family: 'Segoe UI'; font-size: 13px; }
QListWidget { background: #161925; border: 0; padding: 10px; }
QListWidget::item { padding: 10px; border-radius: 6px; }
QListWidget::item:selected { background: #4C1D95; color: #F3F4F6; }
QLabel#title { font-size: 24px; font-weight: 600; }
QLabel#subtitle { color: #9CA3AF; }
QLabel#card { background: #161925; border: 1px solid #2A3045; padding: 18px; border-radius: 8px; }
QPushButton { background: #8B5CF6; padding: 10px 16px; border: 0; border-radius: 6px; }
QPushButton:hover { background: #A78BFA; }
"""


class MainWindow(QMainWindow):
    closed = Signal()

    def __init__(self, settings: Settings, *, supervisor=None, embedded=True):
        super().__init__()
        self.settings = settings
        self.supervisor = supervisor or Supervisor(settings, parent=self)
        self.setWindowTitle("LiveGame Studio · GD01 Foundation")
        self.resize(1280, 850)
        self.setMinimumSize(1000, 700)
        self.setStyleSheet(STYLE)
        self.done = False
        self.web = None
        self.diagnostic = {"state": "not loaded"}
        root = QWidget()
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        self.nav = QListWidget()
        self.nav.addItems(NAVIGATION)
        self.nav.setFixedWidth(220)
        layout.addWidget(self.nav)
        content = QVBoxLayout()
        layout.addLayout(content, 1)
        brand = QLabel("LIVEGAME STUDIO    /    FOUNDATION")
        brand.setObjectName("subtitle")
        content.addWidget(brand)
        self.banner = QLabel("Loading — chờ backend")
        self.banner.setObjectName("card")
        content.addWidget(self.banner)
        self.pages = QStackedWidget()
        content.addWidget(self.pages, 1)
        self.cards = {}
        for name, phase in zip(NAVIGATION, PHASES):
            page = QWidget()
            panel = QVBoxLayout(page)
            title = QLabel(name)
            title.setObjectName("title")
            panel.addWidget(title)
            if name == "Dashboard":
                panel.addWidget(QLabel("Sức khỏe nền tảng · Dữ liệu từ backend cục bộ"))
                for key, value in {
                    "version": f"Application version · {VERSION}",
                    "environment": f"Environment · {settings.environment}",
                    "backend": "Backend · Loading",
                    "sqlite": "SQLite smoke · NOT RUN",
                    "runtime": "Runtime diagnostic · NOT RUN",
                }.items():
                    label = QLabel(value)
                    label.setObjectName("card")
                    self.cards[key] = label
                    panel.addWidget(label)
                preview_button = QPushButton("Mở Foundation Demo · 9:16")
                preview_button.clicked.connect(lambda: self.nav.setCurrentRow(2))
                panel.addWidget(preview_button)
            elif name == "Live Studio":
                panel.addWidget(QLabel("Foundation Demo 9:16 · Live Studio đầy đủ: Planned (GD18)"))
                self.runtime_label = QLabel("Runtime · Loading")
                self.runtime_label.setWordWrap(True)
                panel.addWidget(self.runtime_label)
                if embedded:
                    try:
                        from PySide6.QtWebEngineWidgets import QWebEngineView

                        self.web = QWebEngineView()
                        self.web.loadFinished.connect(self.loaded)
                        panel.addWidget(self.web, 1)
                    except ImportError:
                        self.runtime_label.setText("QWebEngine unavailable — dùng browser preview")
                browser = QPushButton("Mở browser preview")
                browser.clicked.connect(
                    lambda: QDesktopServices.openUrl(QUrl(settings.runtime_url))
                )
                panel.addWidget(browser)
            elif name == "Settings":
                panel.addWidget(
                    QLabel(
                        f"Environment: {settings.environment}\nBackend: {settings.backend_url}\n"
                        f"Preview: {settings.runtime_url}\n\nCấu hình qua .env / LGS_*; khởi động lại để áp dụng.\n"
                        "Settings editor: Planned / Not implemented in GD01 (GD03)."
                    )
                )
            else:
                text = f"Planned / Not implemented in GD01 · Sắp ra mắt ({phase})"
                if name == "Game Library":
                    text = (
                        "GAME001 · Tu Tiên Online\ncultivation_online · Danh mục dự kiến, chưa thể chơi.\n\n"
                        + text
                    )
                label = QLabel(text)
                label.setObjectName("card")
                panel.addWidget(label)
            if name != "Live Studio":
                panel.addStretch()
            self.pages.addWidget(page)
        self.nav.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.nav.setCurrentRow(0)
        self.supervisor.backend_status.connect(self.update_backend)
        self.supervisor.runtime_ready.connect(self.open_runtime)
        self.supervisor.runtime_error.connect(self.runtime_failure)
        self.supervisor.stopped.connect(self.finish_close)
        self.diagnostic_timer = QTimer(self)
        self.diagnostic_timer.setInterval(1200)
        self.diagnostic_timer.timeout.connect(self.inspect_runtime)

    def start(self):
        self.supervisor.start()

    def update_backend(self, status, data):
        self.banner.setText(status)
        self.banner.setStyleSheet("color: #10B981" if status == "Connected" else "color: #F59E0B")
        self.cards["backend"].setText("Backend · " + status)
        self.cards["version"].setText(f"Application version · {data.get('version', VERSION)}")
        smoke = "PASS" if data.get("db_smoke_ok") else ("FAIL" if data else "UNAVAILABLE")
        self.cards["sqlite"].setText("SQLite smoke · " + smoke)

    def runtime_failure(self, message):
        self.runtime_label.setText(message)
        self.cards["runtime"].setText(message)

    def open_runtime(self):
        if self.web:
            self.web.setUrl(QUrl(self.settings.runtime_url))
        else:
            self.runtime_failure("Browser preview available; embedded WebGL NOT RUN")

    def loaded(self, ok):
        if ok:
            self.diagnostic_timer.start()
            self.inspect_runtime()
        else:
            self.runtime_failure("Embedded preview load failed; thử browser preview")

    def inspect_runtime(self):
        if self.web and not self.done:
            self.web.page().runJavaScript(
                "JSON.stringify(window.foundation?.diagnostics() ?? {state:'loading'})",
                self.receive_diagnostic,
            )

    def receive_diagnostic(self, value):
        try:
            self.diagnostic = json.loads(value)
            state = self.diagnostic.get("state", "unknown")
            label = f"Embedded WebGL · {state} · frames: {self.diagnostic.get('frames', 0)}"
            self.runtime_label.setText(label)
            self.cards["runtime"].setText(label)
        except (ValueError, TypeError):
            self.runtime_failure("Runtime diagnostic unavailable")

    def closeEvent(self, event):
        if self.done:
            event.accept()
            self.closed.emit()
            return
        event.ignore()
        self.diagnostic_timer.stop()
        self.banner.setText("Stopping owned processes…")
        if self.web:
            self.web.page().runJavaScript("window.foundation?.dispose()")
            self.web.setUrl(QUrl("about:blank"))
        self.supervisor.stop()

    def finish_close(self):
        self.done = True
        # Defer: stop() may emit synchronously inside closeEvent; Qt ignores a reentrant close.
        QTimer.singleShot(0, self.close)
