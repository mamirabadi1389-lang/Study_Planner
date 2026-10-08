"""JSON API: courses, schedule, tasks, reminders, exams, progress."""
from __future__ import annotations

import re
import sqlite3
from datetime import date, datetime

from flask import Blueprint, abort, jsonify, request

from ..database import get_db
from ..services import progress

bp = Blueprint("api", __name__, url_prefix="/api")

_COLOR = re.compile(r"#[0-9a-fA-F]{6}")
_TIME = re.compile(r"\d{2}:\d{2}")
_MINUTE = "%Y-%m-%dT%H:%M"

_EXAM_SQL = (
    "SELECT e.id, e.title, e.day, e.grade, e.max_grade, "
    "c.id AS course_id, c.name AS course, c.color, c.credits "
    "FROM exams e JOIN courses c ON c.id = e.course_id"
)
_SLOT_SQL = (
    'SELECT s.id, s.weekday, s.start, s."end" AS "end", '
    "c.id AS course_id, c.name, c.color "
    "FROM schedule s JOIN courses c ON c.id = s.course_id"
)


# ---------------------------------------------------------------- helpers
def _rows(sql: str, args: tuple = ()) -> list[dict]:
    return [dict(r) for r in get_db().execute(sql, args).fetchall()]


def _body(*required: str) -> dict:
    data = request.get_json(silent=True) or {}
    for key in required:
        if data.get(key) in (None, ""):
            abort(400, description="اطلاعات ناقص است")
    return data


def _day(value: str | None) -> str:
    try:
        if not value:
            return date.today().isoformat()
        return date.fromisoformat(str(value)).isoformat()
    except ValueError:
        abort(400, description="تاریخ نامعتبر است")


def _time(value: object) -> str:
    if not _TIME.fullmatch(str(value)):
        abort(400, description="ساعت نامعتبر است")
    return str(value)


def _int(value: object, default: int, low: int, high: int) -> int:
    try:
        return min(max(int(value), low), high)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def _num(value: object, default: float) -> float:
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default
    return number if number > 0 else default


def _insert(sql: str, args: tuple):
    db = get_db()
    cur = db.execute(sql, args)
    db.commit()
    return jsonify(id=cur.lastrowid), 201


def _write(sql: str, args: tuple):
    db = get_db()
    db.execute(sql, args)
    db.commit()
    return jsonify(ok=True)


def _delete(table: str, row_id: int):
    # `table` is always a literal from this module, never user input.
    return _write(f"DELETE FROM {table} WHERE id = ?", (row_id,))


@bp.errorhandler(400)
def _bad_request(err):
    return jsonify(error=err.description), 400


@bp.errorhandler(sqlite3.IntegrityError)
def _integrity(_err):
    return jsonify(error="مرجع نامعتبر است"), 400


# ---------------------------------------------------------------- courses
@bp.get("/courses")
def courses():
    return jsonify(_rows("SELECT * FROM courses ORDER BY name"))


@bp.post("/courses")
def add_course():
    data = _body("name")
    color = str(data.get("color", ""))
    if not _COLOR.fullmatch(color):
        color = "#7c5cff"
    return _insert(
        "INSERT INTO courses (name, color, credits) VALUES (?, ?, ?)",
        (str(data["name"]).strip(), color, _int(data.get("credits"), 1, 1, 10)),
    )


@bp.delete("/courses/<int:row_id>")
def del_course(row_id: int):
    return _delete("courses", row_id)


@bp.get("/schedule")
def schedule():
    return jsonify(_rows(_SLOT_SQL + " ORDER BY s.weekday, s.start"))


@bp.post("/schedule")
def add_slot():
    data = _body("course_id", "weekday", "start", "end")
    return _insert(
        "INSERT INTO schedule (course_id, weekday, start, \"end\") "
        "VALUES (?, ?, ?, ?)",
        (
            _int(data["course_id"], 0, 0, 10**9),
            _int(data["weekday"], 0, 0, 6),
            _time(data["start"]),
            _time(data["end"]),
        ),
    )


@bp.delete("/schedule/<int:row_id>")
def del_slot(row_id: int):
    return _delete("schedule", row_id)


@bp.get("/tasks")
def tasks():
    day = _day(request.args.get("day"))
    return jsonify(
        _rows(
            "SELECT * FROM tasks WHERE day = ? ORDER BY done, priority, id",
            (day,),
        )
    )


@bp.post("/tasks")
def add_task():
    data = _body("title")
    return _insert(
        "INSERT INTO tasks (title, day, priority) VALUES (?, ?, ?)",
        (
            str(data["title"]).strip(),
            _day(data.get("day")),
            _int(data.get("priority"), 2, 1, 3),
        ),
    )


@bp.patch("/tasks/<int:row_id>")
def patch_task(row_id: int):
    data = _body("done")
    return _write(
        "UPDATE tasks SET done = ? WHERE id = ?",
        (1 if data["done"] else 0, row_id),
    )


@bp.delete("/tasks/<int:row_id>")
def del_task(row_id: int):
    return _delete("tasks", row_id)


@bp.get("/reminders")
def reminders():
    return jsonify(
        _rows("SELECT * FROM reminders ORDER BY fired, due_at LIMIT 30")
    )


@bp.post("/reminders")
def add_reminder():
    data = _body("title", "due_at")
    try:
        due = datetime.fromisoformat(str(data["due_at"])).strftime(_MINUTE)
    except ValueError:
        abort(400, description="زمان نامعتبر است")
    return _insert(
        "INSERT INTO reminders (title, due_at) VALUES (?, ?)",
        (str(data["title"]).strip(), due),
    )


@bp.post("/reminders/poll")
def poll_reminders():
    """Return due reminders and mark them as fired."""
    now = datetime.now().strftime(_MINUTE)
    due = _rows(
        "SELECT * FROM reminders WHERE fired = 0 AND due_at <= ?", (now,)
    )
    if due:
        db = get_db()
        db.executemany(
            "UPDATE reminders SET fired = 1 WHERE id = ?",
            [(r["id"],) for r in due],
        )
        db.commit()
    return jsonify(due)


@bp.delete("/reminders/<int:row_id>")
def del_reminder(row_id: int):
    return _delete("reminders", row_id)


@bp.get("/exams")
def exams():
    return jsonify(_rows(_EXAM_SQL + " ORDER BY e.day"))


@bp.post("/exams")
def add_exam():
    data = _body("course_id", "title", "day")
    return _insert(
        "INSERT INTO exams (course_id, title, day, max_grade) "
        "VALUES (?, ?, ?, ?)",
        (
            _int(data["course_id"], 0, 0, 10**9),
            str(data["title"]).strip(),
            _day(data["day"]),
            _num(data.get("max_grade"), 20.0),
        ),
    )


@bp.patch("/exams/<int:row_id>")
def patch_exam(row_id: int):
    grade = (request.get_json(silent=True) or {}).get("grade")
    if grade is not None:
        try:
            grade = float(grade)
        except (TypeError, ValueError):
            abort(400, description="نمره نامعتبر است")
        if grade < 0:
            abort(400, description="نمره نامعتبر است")
    return _write("UPDATE exams SET grade = ? WHERE id = ?", (grade, row_id))


@bp.delete("/exams/<int:row_id>")
def del_exam(row_id: int):
    return _delete("exams", row_id)


@bp.get("/summary")
def summary():
    today = date.today()
    weekday = (today.weekday() + 2) % 7 
    all_exams = _rows(_EXAM_SQL + " ORDER BY e.day")
    done = get_db().execute(
        "SELECT COUNT(*) FROM tasks WHERE done = 1"
    ).fetchone()[0]

    focus = get_db().execute(
        "SELECT COALESCE(SUM(minutes), 0) FROM focus_sessions"
    ).fetchone()[0]

    upcoming = [
        e for e in all_exams
        if e["grade"] is None and e["day"] >= today.isoformat()
    ]
    next_exam = None
    if upcoming:
        left = (date.fromisoformat(upcoming[0]["day"]) - today).days
        next_exam = {**upcoming[0], "days_left": left}

    return jsonify(
        today=today.isoformat(),
        weekday=weekday,
        classes=_rows(
            _SLOT_SQL + " WHERE s.weekday = ? ORDER BY s.start", (weekday,)
        ),
        tasks=_rows(
            "SELECT * FROM tasks WHERE day = ? ORDER BY done, priority, id",
            (today.isoformat(),),
        ),
        next_exam=next_exam,
        gpa=progress.gpa(all_exams),
        progress=progress.level_info(
            progress.total_xp(done, all_exams, focus)
        ),
        courses=progress.course_averages(all_exams),
    )