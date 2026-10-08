"""Progress, grade, level, streak and achievement calculations."""
from __future__ import annotations

from datetime import date, timedelta

XP_PER_TASK = 10
XP_PER_EXAM = 50
XP_PER_LEVEL = 100
FOCUS_MIN_PER_XP = 5
SCALE = 20.0
LEVELS_PER_RANK = 3
RANKS = ("تازه‌کار", "کوشا", "پرتلاش", "حرفه‌ای", "استاد", "افسانه")


def score20(exam: dict) -> float:
    """Return the exam grade normalised to a 0-20 scale."""
    return exam["grade"] / exam["max_grade"] * SCALE


def gpa(exams: list[dict]) -> float | None:
    """Credit-weighted average of all graded exams."""
    graded = [e for e in exams if e["grade"] is not None]
    weight = sum(e["credits"] for e in graded)
    if not weight:
        return None
    total = sum(score20(e) * e["credits"] for e in graded)
    return round(total / weight, 2)


def course_averages(exams: list[dict]) -> list[dict]:
    """Average score per course (graded exams only)."""
    buckets: dict[int, dict] = {}
    for exam in exams:
        if exam["grade"] is None:
            continue
        bucket = buckets.setdefault(
            exam["course_id"],
            {"course": exam["course"], "color": exam["color"], "scores": []},
        )
        bucket["scores"].append(score20(exam))
    return [
        {
            "course": b["course"],
            "color": b["color"],
            "count": len(b["scores"]),
            "average": round(sum(b["scores"]) / len(b["scores"]), 2),
        }
        for b in buckets.values()
    ]


def total_xp(
    done_tasks: int, exams: list[dict], focus_minutes: int = 0
) -> int:
    """XP from finished tasks, graded exams and focus time."""
    xp = done_tasks * XP_PER_TASK + focus_minutes // FOCUS_MIN_PER_XP
    for exam in exams:
        if exam["grade"] is not None:
            xp += round(exam["grade"] / exam["max_grade"] * XP_PER_EXAM)
    return xp


def level_info(xp: int) -> dict:
    """Level, rank and percent towards the next level."""
    level = xp // XP_PER_LEVEL + 1
    rank = RANKS[min((level - 1) // LEVELS_PER_RANK, len(RANKS) - 1)]
    return {
        "xp": xp,
        "level": level,
        "rank": rank,
        "percent": xp % XP_PER_LEVEL * 100 // XP_PER_LEVEL,
    }


def streaks(done_by_day: dict[str, int], today: date) -> tuple[int, int]:
    """Return (current, best) streak of days with a finished task."""
    day = today
    if not done_by_day.get(day.isoformat()):
        day -= timedelta(days=1)  # an unfinished today does not break it
    current = 0
    while done_by_day.get(day.isoformat()):
        current += 1
        day -= timedelta(days=1)

    best = run = 0
    previous: date | None = None
    for key in sorted(k for k, v in done_by_day.items() if v):
        current_day = date.fromisoformat(key)
        if previous and (current_day - previous).days == 1:
            run += 1
        else:
            run = 1
        best = max(best, run)
        previous = current_day
    return current, best


def _minutes(clock: str) -> int:
    hours, minutes = clock.split(":")
    return int(hours) * 60 + int(minutes)


def slot_hours(slots: list[dict]) -> list[dict]:
    """Weekly class hours per course."""
    buckets: dict[int, dict] = {}
    for slot in slots:
        length = _minutes(slot["end"]) - _minutes(slot["start"])
        if length <= 0:
            continue
        bucket = buckets.setdefault(
            slot["course_id"],
            {"course": slot["name"], "color": slot["color"], "minutes": 0},
        )
        bucket["minutes"] += length
    items = [{**b, "hours": round(b["minutes"] / 60, 2)} for b in buckets.values()]
    return sorted(items, key=lambda i: i["minutes"], reverse=True)


def achievements(
    tasks_done: int,
    best_streak: int,
    graded: int,
    gpa_value: float | None,
    focus_minutes: int,
) -> list[dict]:
    """Badge list with unlocked flags."""
    rules = (
        ("🌱", "اولین قدم", "یک کار رو تموم کن", tasks_done >= 1),
        ("🔟", "ده‌تایی", "۱۰ کار انجام بده", tasks_done >= 10),
        ("🏭", "ماشین کار", "۵۰ کار انجام بده", tasks_done >= 50),
        ("🔥", "سه روز پیاپی", "۳ روز پشت‌سرهم کار تموم کن", best_streak >= 3),
        ("⚡", "هفته بی‌وقفه", "۷ روز پشت‌سرهم", best_streak >= 7),
        ("🎯", "اولین نمره", "یک نمره ثبت کن", graded >= 1),
        ("🏆", "درخشان", "معدل ۱۷ یا بالاتر", bool(gpa_value and gpa_value >= 17)),
        ("⏱️", "تمرکز ۱۰ ساعته", "۱۰ ساعت تمرکز", focus_minutes >= 600),
    )
    return [
        {"icon": icon, "title": title, "desc": desc, "unlocked": ok}
        for icon, title, desc, ok in rules
    ]