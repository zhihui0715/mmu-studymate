"""game.py - the rules of StudyMate (no Flask, no database, just Python).

Shared file: each member edits ONLY their own marked section.
"""
from datetime import date                   # built-in: dates


# ---------- [OWNER: Kong Fu Sheng] task scoring ----------
# task_score = priority weight x urgency x subject weight   (proposal formula)

PRIORITY_WEIGHT = {'Low': 1, 'Medium': 2, 'High': 3, 'Critical': 4}
HEAVY_TYPES = ('Exam', 'Test', 'Project')   # count extra in exam weeks (stage, used from W6)
OVERDUE_STEP = 0.1                          # extra urgency per day late
OVERDUE_MAX_DAYS = 10                       # late days stop counting after this (max urgency 2.0)


def days_until(date_text, today):
    """Whole days from today. Negative = already passed."""
    return (date.fromisoformat(date_text) - today).days


def urgency(days_left):
    """Due today = 1.0, tomorrow = 0.5, in 3 days = 0.25. Late tasks go above 1.0, capped at 2.0."""
    if days_left < 0:
        return 1.0 + OVERDUE_STEP * min(-days_left, OVERDUE_MAX_DAYS)
    return 1 / (days_left + 1)              # +1 so "due today" never divides by zero


def task_score(task, today, stage=1.0):
    """`task` needs: priority, due, subject_weight (and type). Heavy types are multiplied by `stage`."""
    boost = stage if task.get('type') in HEAVY_TYPES else 1.0
    return PRIORITY_WEIGHT[task['priority']] * urgency(days_until(task['due'], today)) * task['subject_weight'] * boost