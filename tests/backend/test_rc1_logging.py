import pytest

from core.logging import redact


@pytest.mark.parametrize(
    "message, secret",
    [
        ("Authorization: Basic cmMxLXByaXZhdGU=", "cmMxLXByaXZhdGU="),
        ("Cookie: session=rc1-first; refresh=rc1-second", "rc1-second"),
    ],
)
def test_complete_sensitive_header_redaction(message, secret):
    assert secret not in redact(message)


def test_uvicorn_exception_console_redacts_runtime_credentials(managed_backend, tmp_path):
    script = tmp_path / "fault_server.py"
    script.write_text(
        """
from apps.backend import __main__ as backend
from apps.backend.main import create_app
from pydantic import SecretStr

def factory(settings):
    app = create_app(settings)
    app.state.core.credentials.admin = SecretStr("rc1-fake-private-credential")
    @app.get("/test-fault")
    def fault():
        raise RuntimeError(app.state.core.credentials.admin.get_secret_value())
    return app

backend.create_app = factory
raise SystemExit(backend.main())
""",
        encoding="utf-8",
    )
    with managed_backend(script=script) as backend:
        response = backend.client.get("/test-fault")
        assert response.status_code == 500
        assert "rc1-fake-private-credential" not in response.text
    assert backend.exit_code == 0
    assert "rc1-fake-private-credential" not in backend.output
    assert "[REDACTED]" in backend.output
