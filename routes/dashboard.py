"""routes/dashboard.py - the Dashboard page.                     [OWNER: Kong Fu Sheng]

W3: page shell: greeting, the four task counters (Tan's list_tasks) and the study hours card
    (journal hours = what you studied, task est_hours = what your tasks need).
Later: today's top 3 (W4), trimester week bar (W5), weekly workload (W6), journal reminder.
This page only READS data, it never changes it.
"""
from datetime import datetime, timedelta         # built-in: the current hour, day maths

from flask import Blueprint, g, render_template

import database
import game
from helpers import login_required

bp = Blueprint('dashboard', __name__)            # page names start with 'dashboard.'


@bp.route('/dashboard')
@login_required
def dashboard():
    tasks = database.list_tasks(g.user['id'])
    open_tasks = [t for t in tasks if t['status'] != 'done']
    days = lambda t: game.days_until(t['due'], g.today)    # a tiny function: days until this task is due

    # The four number cards
    stats = {
        'today': sum(1 for t in open_tasks if days(t) == 0),
        'week': sum(1 for t in open_tasks if 0 < days(t) <= 7),
        'overdue': sum(1 for t in open_tasks if days(t) < 0),
        'done': sum(1 for t in tasks if t['status'] == 'done'),
    }
    # Study hours: what you did (journal, last 7 days) vs what your tasks need (est_hours, next 7 days)
    week_start = (g.today - timedelta(days=6)).isoformat()
    hours = {
        'studied': database.journal_hours_between(g.user['id'], week_start, g.today.isoformat()),
        'needed': sum(t['est_hours'] for t in open_tasks if 0 <= days(t) <= 7),
    }

    hour = datetime.now().hour
    greeting = 'Good morning' if hour < 12 else 'Good afternoon' if hour < 18 else 'Good evening'
    return render_template('dashboard.html', greeting=greeting, stats=stats, hours=hours)
