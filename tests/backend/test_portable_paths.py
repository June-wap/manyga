import sqlite3
from contextlib import closing

import pytest
from pydantic import ValidationError

from core import config
from core.config import Settings
from core.sqlite_smoke import connect, run_smoke


def test_user_profiles_use_independent_unicode_smoke_databases(monkeypatch, tmp_path):
    roots = [tmp_path / "Máy A - Người dùng An", tmp_path / "Máy B - Người dùng Bình"]
    settings = []
    for root in roots:
        monkeypatch.setenv("LOCALAPPDATA", str(root))
        local = Settings(_env_file=None)
        assert run_smoke(local.db_path)["persistent"]
        settings.append(local)
    assert settings[0].db_path != settings[1].db_path
    with closing(connect(settings[0].db_path)) as db, db:
        db.execute("INSERT INTO foundation_smoke VALUES (2, 'only A')")
    with closing(connect(settings[1].db_path)) as db:
        assert db.execute("SELECT value FROM foundation_smoke WHERE id=2").fetchone() is None
        tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert tables == {"foundation_smoke", "foundation_smoke_child"}
    # Reinitializing the smoke must preserve existing rows rather than recreate the DB.
    run_smoke(settings[0].db_path)
    with closing(sqlite3.connect(settings[0].db_path)) as db:
        assert db.execute("SELECT value FROM foundation_smoke WHERE id=2").fetchone() == ("only A",)


def test_installation_relocation_does_not_change_user_data(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "Local App Data"))
    before = Settings(_env_file=None)
    previous_installation = before.installation_dir
    monkeypatch.setattr(config, "PROJECT_ROOT", tmp_path / "Program Files/Phần mềm mới")
    monkeypatch.chdir(tmp_path)
    after = Settings(_env_file=None)
    assert after.db_path == before.db_path
    assert after.log_dir == before.log_dir
    assert after.installation_dir != previous_installation
    assert not after.installation_dir.exists()


def test_path_layout_and_explicit_data_root(tmp_path):
    settings = Settings(_env_file=None, data_dir=tmp_path / "Dữ liệu riêng")
    directories = [
        settings.database_dir,
        settings.config_dir,
        settings.asset_dir,
        settings.cache_dir,
        settings.log_dir,
    ]
    assert len(set(directories)) == 5
    assert all(path.parent == settings.data_dir for path in directories)
    assert not settings.data_dir.exists()  # Resolving config has no initialization side effect.


@pytest.mark.parametrize(
    "field", ["data_dir", "db_path", "log_dir", "config_dir", "asset_dir", "cache_dir"]
)
def test_unc_paths_rejected_before_network_access(field):
    with pytest.raises(ValidationError, match="Network-share"):
        Settings(_env_file=None, **{field: r"\\server\share\data"})


def test_relative_localappdata_rejected(monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", "relative/user")
    with pytest.raises(ValueError, match="absolute local directory"):
        Settings(_env_file=None)
