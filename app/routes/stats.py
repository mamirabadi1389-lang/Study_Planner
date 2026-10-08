"""Stats, settings and focus-session routes."""
from __future__ import annotations

from datetime import date, timedelta

from flask import Blueprint, abort, jsonify, request

from .. import config
from ..database import get_db
from ..services import progress, settings
from .api import _EXAM_SQL, _SLOT_SQL, _rows

bp = Blueprint("stats", __name__, url_prefix="/api")

HEAT_DAYS = 84


def _clamp(value: object, default: int, low: int, high: int) -> int:
    try:
        return min(max(int(value), low), high)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


@bp.errorhandler(400)
def _bad_request(err):
    return jsonify(error=err.description), 400


# --------------------------------------------------------------- settings
@bp.get("/settings")
def get_settings():
    return jsonify(settings.load())


@bp.put("/settings")
def put_settings():
    data = request.get_json(silent=True) or {}
    clean: dict[str, str] = {}
    if "theme" in data:
        if data["theme"] not in config.THEMES:
            abort(400, description="تم نامعتبر است")
        clean["theme"] = data["theme"]
    if "name" in data:
        clean["name"] = str(data["name"]).strip()[:30]
    if "daily_goal" in data:
        clean["daily_goal"] = str(_clamp(data["daily_goal"], 5, 1, 50))
    if "focus_minutes" in data:
        clean["focus_minutes"] = str(_clamp(data["focus_minutes"], 25, 5, 120))
    settings.save(clean)
    return jsonify(settings.load())


# ------------------------------------------------------------------ focus
@bp.post("/focus")
def add_focus():
    data = request.get_json(silent=True) or {}
    minutes = _clamp(data.get("minutes"), 0, 1, 240)
    if minutes < 1:
        abort(400, description="مدت نامعتبر است")
    db = get_db()
    db.execute(
        "INSERT INTO focus_sessions (day, minutes) VALUES (?, ?)",
        (date.today().isoformat(), minutes),
    )
    db.commit()
    return jsonify(ok=True), 201


# ------------------------------------------------------------------ stats
@bp.get("/stats")
def stats():
    db = get_db()
    today = date.today()
    start = today - timedelta(days=HEAT_DAYS - 1)

    per_day = {
        r["day"]: r
        for r in db.execute(
            "SELECT day, COUNT(*) AS total, SUM(done) AS done "
            "FROM tasks WHERE day >= ? GROUP BY day",
            (start.isoformat(),),
        )
    }
    focus_day = {
        r["day"]: r["minutes"]
        for r in db.execute(
            "SELECT day, SUM(minutes) AS minutes FROM focus_sessions "
            "WHERE day >= ? GROUP BY day",
            (start.isoformat(),),
        )
    }
    days = []
    for i in range(HEAT_DAYS):
        key = (start + timedelta(days=i)).isoformat()
        row = per_day.get(key)
        days.append(
            {
                "day": key,
                "done": row["done"] if row else 0,
                "total": row["total"] if row else 0,
                "focus": focus_day.get(key, 0),
            }
        )

    done_by_day = {
        r["day"]: r["n"]
        for r in db.execute(
            "SELECT day, COUNT(*) AS n FROM tasks WHERE done = 1 GROUP BY day"
        )
    }
    current, best = progress.streaks(done_by_day, today)

    tasks_done = sum(done_by_day.values())
    tasks_total = db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    focus_total = db.execute(
        "SELECT COALESCE(SUM(minutes), 0) FROM focus_sessions"
    ).fetchone()[0]

    exams = _rows(_EXAM_SQL + " ORDER BY e.day")
    graded = [e for e in exams if e["grade"] is not None]
    scores = [
        {
            "day": e["day"],
            "title": e["title"],
            "course": e["course"],
            "color": e["color"],
            "score": round(progress.score20(e), 2),
        }
        for e in graded
    ]

    return jsonify(
        days=days,
        streak={"current": current, "best": best},
        hours=progress.slot_hours(_rows(_SLOT_SQL)),
        scores=scores,
        totals={
            "tasks_done": tasks_done,
            "tasks_total": tasks_total,
            "exams": len(exams),
            "graded": len(graded),
            "focus_minutes": focus_total,
        },
        achievements=progress.achievements(
            tasks_done, best, len(graded), progress.gpa(exams), focus_total
        ),
    )