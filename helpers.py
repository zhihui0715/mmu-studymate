"""helpers.py - small tools the route files share.

Shared file: each member edits ONLY their own marked section.
"""
import math                                 # built-in: isfinite()
import re                                   # built-in: pattern matching
from datetime import date                   # built-in: dates
from functools import wraps                 # built-in: keeps a function's name when wrapping it

from flask import g, redirect, request, url_for


# ---------- [OWNER: Zhi Hui] login and form input ----------

def login_required(view):
    """Put @login_required above a route to make it members-only (装饰器 decorator)."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:                  # nobody logged in
            return redirect(url_for('account.login'))
        return view(*args, **kwargs)
    return wrapped


def is_valid_email(email):
    """something@something.something, at most 254 characters."""
    return bool(re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email)) and len(email) <= 254


def parse_date(text):
    """'2026-10-05' -> date(2026, 10, 5). None if it is not a real date."""
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', text or ''):
        return None
    try:
        return date.fromisoformat(text)
    except ValueError:                      # e.g. 2026-02-31
        return None


def form_text(name, limit=500):
    """One text box from the form: spaces trimmed, cut to `limit` characters."""
    return (request.form.get(name) or '').strip()[:limit]


def redirect_back(default='dashboard.dashboard'):     # W3
    """Sends the user back to the page the form was on (the hidden 'next' field, from W4).
    Only addresses inside our own site are accepted (one leading '/'), so a fake form
    cannot send the user to another website (open redirect)."""
    target = request.form.get('next', '')
    if target.startswith('/') and not target.startswith('//') and '\\' not in target:
        return redirect(target)
    return redirect(url_for(default))


# ---------- [OWNER: Tan Yu Zhe] subject input ----------

def parse_weight(text):
    """Subject weight: above 0 and at most 3. None if not."""
    try:
        weight = float(text)
    except (TypeError, ValueError):
        return None
    return weight if 0 < weight <= 3 and math.isfinite(weight) else None   # blocks 'nan' and 'inf'


# ---------- [OWNER: Tan Yu Zhe] task input (W3) ----------

MAX_EST_HOURS = 40                          # the longest study estimate one task may have


def parse_hours(text, low=0.0, high=MAX_EST_HOURS):
    """'2.5' -> 2.5. Empty means 0. None if it is not a number from low to high."""
    text = (text or '').strip()
    if not text:
        return 0.0
    try:
        value = float(text)
    except ValueError:
        return None
    return round(value, 2) if math.isfinite(value) and low <= value <= high else None
