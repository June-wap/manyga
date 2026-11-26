import pytest

from core.config import Settings


@pytest.fixture
def settings(tmp_path):
    return Settings(
        _env_file=None,
        environment="test",
        data_dir=tmp_path / "data",
        log_dir=tmp_path / "logs",
        db_path=tmp_path / "smoke.sqlite3",
    )
