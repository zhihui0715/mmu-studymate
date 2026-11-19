"""check_mmu.py - automatic checks. Run before every pull request:  python check_mmu.py

Each member adds checks in their own section. W2: Kong's urgency and task_score checks.
"""
from datetime import date

import game


def close(a, b):
    """Equal, ignoring tiny rounding."""
    return abs(a - b) < 1e-9


# ---------- [OWNER: Kong Fu Sheng] urgency and task_score ----------
TODAY = date(2026, 11, 20)

assert close(game.urgency(0), 1.0) and close(game.urgency(1), 0.5) and close(game.urgency(3), 0.25)
assert game.urgency(-1) > game.urgency(0)                       # late is more urgent than due today
assert close(game.urgency(-10), 2.0) and close(game.urgency(-400), 2.0)   # capped

# Worked example 1: High, due tomorrow, subject weight 2  ->  3 x 0.5 x 2 = 3.0
ex1 = {'priority': 'High', 'due': '2026-11-21', 'subject_weight': 2, 'type': 'Assignment'}
assert close(game.task_score(ex1, TODAY), 3.0)

# Worked example 2: Critical exam, due in 3 days, weight 1.5, exam stage 1.5  ->  4 x 0.25 x 1.5 x 1.5 = 2.25
ex2 = {'priority': 'Critical', 'due': '2026-11-23', 'subject_weight': 1.5, 'type': 'Exam'}
assert close(game.task_score(ex2, TODAY, stage=1.5), 2.25)
assert close(game.task_score(ex2, TODAY), 1.5)                  # no stage: no boost

print('check_mmu.py: all checks passed')
