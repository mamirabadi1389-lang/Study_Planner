"""SQLite access layer and schema."""
import sqlite3

from flask import Flask, g

from .config import DATA_DIR, DATABASE_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS courses (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT NOT NULL,
    color   TEXT NOT NULL DEFAULT '#7c5cff',
    credits INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS schedule (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    weekday   INTEGER NOT NULL CHECK (weekday BETWEEN 0 AND 6),
    start     TEXT NOT NULL,
    end       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    title    TEXT NOT NULL,
    day      TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 2,
    done     INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS reminders (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    title  TEXT NOT NULL,
    due_at TEXT NOT NULL,
    fired  INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS exams (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    title     TEXT NOT NULL,
    day       TEXT NOT NULL,
    grade     REAL,
    max_grade REAL NOT NULL DEFAULT 20
);

CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS focus_sessions (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    day     TEXT NOT NULL,
    minutes INTEGER NOT NULL
);
"""


def get_db() -> sqlite3.Connection:
    """Return the per-request database connection."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_error: BaseException | None = None) -> None:
    """Close the connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    """Create the data folder and all tables."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.executescript(SCHEMA)


def init_app(app: Flask) -> None:
    """Hook the database into the Flask app."""
    app.teardown_appcontext(close_db)
    init_db()