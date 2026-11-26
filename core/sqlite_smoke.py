"""Isolated smoke database only; no production models or write coordinator."""

import sqlite3
from contextlib import closing
from pathlib import Path


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=5)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA busy_timeout=5000")
    return db


def run_smoke(path: Path) -> dict:
    with closing(connect(path)) as db:
        with db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS foundation_smoke (id INTEGER PRIMARY KEY, value TEXT)"
            )
            db.execute("INSERT OR REPLACE INTO foundation_smoke VALUES (1, ?)", ("Tiếng Việt",))
        with db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS foundation_smoke_child (parent_id INTEGER REFERENCES foundation_smoke(id))"
            )
            try:
                db.execute("INSERT INTO foundation_smoke_child VALUES (-1)")
            except sqlite3.IntegrityError:
                pass
            else:
                raise RuntimeError("Foreign key enforcement failed")
        db.execute("UPDATE foundation_smoke SET value='rollback' WHERE id=1")
        db.rollback()
        properties = {
            "wal": db.execute("PRAGMA journal_mode").fetchone()[0] == "wal",
            "foreign_keys": db.execute("PRAGMA foreign_keys").fetchone()[0] == 1,
            "busy_timeout_ms": db.execute("PRAGMA busy_timeout").fetchone()[0],
            "sqlite_version": sqlite3.sqlite_version,
        }
    with closing(connect(path)) as reopened:
        properties["persistent"] = (
            reopened.execute("SELECT value FROM foundation_smoke WHERE id=1").fetchone()[0]
            == "Tiếng Việt"
        )
    if not all(properties[k] for k in ("wal", "foreign_keys", "persistent")):
        raise RuntimeError("SQLite foundation smoke failed")
    return properties
