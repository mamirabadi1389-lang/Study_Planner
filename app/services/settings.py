"""Settings stored in the database."""
from __future__ import annotations

from ..config import DEFAULT_SETTINGS
from ..database import get_db


def load() -> dict[str, str]:
    """Return all settings, filling gaps with defaults."""
    rows = get_db().execute("SELECT key, value FROM settings").fetchall()
    stored = {row["key"]: row["value"] for row in rows}
    return {**DEFAULT_SETTINGS, **stored}


def save(values: dict[str, str]) -> None:
    """Insert or update the given settings."""
    db = get_db()
    db.executemany(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        list(values.items()),
    )
    db.commit()