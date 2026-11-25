"""routes/journal.py - the daily journal.                     [OWNER: Kong Fu Sheng]

W2: mood, what went well, what to improve, study hours. One entry per day; past days editable.
Later: journal XP (W7, with Zhi Hui), task counts (W4), planner and insights.
"""
import math                                      # built-in: isfinite()

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

import database
from data import MOOD_FACES, MOODS
from helpers import form_text, login_required, parse_date

bp = Blueprint('journal', __name__)


def render_journal(day, entry, error=''):
    return render_template('journal.html', day=day, entry=entry or {}, error=error,
                           mood_faces=MOOD_FACES, moods=MOODS,
                           past_days=database.recent_journal(g.user['id']), today=g.today.isoformat())


@bp.route('/journal')
@login_required
def journal():
    chosen = parse_date(request.args.get('date'))
    day = chosen.isoformat() if chosen and chosen <= g.today else g.today.isoformat()   # never a future day
    return render_journal(day, database.get_journal_entry(g.user['id'], day))


@bp.post('/journal')
@login_required
def journal_save():
    chosen = parse_date(request.form.get('date'))
    if chosen is None or chosen > g.today:
        abort(400)
    day = chosen.isoformat() # covert to string for database and template

    mood_text = request.form.get('mood', '')
    try:
        hours = float(request.form.get('hours', 0))
    except ValueError:
        hours = -1                               # not a number: caught by the check below
    entry = {'mood': int(mood_text) if mood_text.isdigit() else 0, 'went_well': form_text('went_well'),
             'improve': form_text('improve'), 'hours': hours}

    if not 1 <= entry['mood'] <= 5:
        return render_journal(day, entry, 'Pick how your day felt first.')
    if not (0 <= hours <= 10 and math.isfinite(hours)):
        return render_journal(day, entry, 'Study hours must be between 0 and 10.')

    is_new = not database.has_journal_entry(g.user['id'], day) # True if this is the first entry for that day
    database.save_journal_entry(g.user['id'], day, entry['mood'], entry['went_well'], entry['improve'], hours)
    flash('Summary saved' if is_new else 'Summary updated')
    return redirect(url_for('journal.journal', date=day))

