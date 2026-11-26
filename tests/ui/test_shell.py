from PySide6.QtCore import QProcess

from apps.desktop.supervisor import Supervisor
from apps.desktop.window import NAVIGATION, MainWindow


def test_navigation_and_unavailable(qtbot, settings):
    supervisor = Supervisor(settings, own_backend=False, own_runtime=False)
    window = MainWindow(settings, supervisor=supervisor, embedded=False)
    qtbot.addWidget(window)
    window.show()
    for i, name in enumerate(NAVIGATION):
        window.nav.setCurrentRow(i)
        assert window.pages.currentIndex() == i
        assert window.nav.currentItem().text() == name
    window.update_backend("Backend Unavailable", {})
    assert "Unavailable" in window.banner.text()
    assert "UNAVAILABLE" in window.cards["sqlite"].text()
    window.update_backend("Connected", {"db_smoke_ok": True, "version": "0.1.0"})
    assert "PASS" in window.cards["sqlite"].text()
    with qtbot.waitSignal(window.closed):
        window.close()


def test_readiness_timeout_real_http(qtbot, settings):
    settings.backend_port = 18971
    settings.runtime_url = "http://127.0.0.1:18972"
    settings.readiness_timeout_s = 0.05
    supervisor = Supervisor(settings, own_backend=False, own_runtime=False)
    observed = []
    supervisor.backend_status.connect(lambda state, data: observed.append(state))
    supervisor.start()
    try:
        qtbot.waitUntil(lambda: any("Unavailable" in value for value in observed), timeout=5000)
    finally:
        supervisor.stop()


def test_owned_backend_start_stop_and_port_conflict(qtbot, settings):
    settings.backend_port = 18973
    supervisor = Supervisor(settings, own_runtime=False)
    observed = []
    supervisor.backend_status.connect(lambda state, data: observed.append(state))
    supervisor.start()
    try:
        qtbot.waitUntil(lambda: "Connected" in observed, timeout=20000)
        assert supervisor.backend.processId() > 0
        other = Supervisor(settings, own_runtime=False)
        conflicts = []
        other.backend_status.connect(lambda state, data: conflicts.append(state))
        other.start()
        assert any("port conflict" in state for state in conflicts)
        other.stop()
        assert supervisor.backend.state() == QProcess.ProcessState.Running
    finally:
        with qtbot.waitSignal(supervisor.stopped, timeout=10000):
            supervisor.stop()
    assert supervisor.backend.exitCode() == 0
    assert supervisor.backend.state() == QProcess.ProcessState.NotRunning
