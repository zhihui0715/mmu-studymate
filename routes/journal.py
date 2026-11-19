"""routes/journal.py - the daily journal.                     [OWNER: Kong Fu Sheng]

W2: mood, what went well, what to improve, study hours. One entry per day; past days editable.
Later: journal XP (W7, with Zhi Hui) and task counts (W4).
"""
import math  # Built-in module used to check valid numbers.

# Flask functions for handling pages, requests, redirects and messages.
from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

import database  # Handles saving and retrieving journal entries.
from data import MOOD_BY_VALUE, MOODS  # Stores mood options and their information.
from helpers import form_text, login_required, parse_date  # Reusable helper functions.

# Creates a Blueprint to organize journal routes.
bp = Blueprint('journal', __name__)


# Displays the journal page with the selected day's information.
def render_journal(day, entry, error=''):
    return render_template(
        'journal.html',
        day=day,  # Sends the selected date to the HTML page.
        entry=entry or {},  # Sends the saved entry or an empty dictionary.
        error=error,  # Sends an error message if validation fails.
        moods=MOODS,  # Sends all available mood options.
        mood_by_value=MOOD_BY_VALUE,  # Matches mood values with their information.
        past_days=database.recent_journal(g.user['id']),  # Retrieves recent journal entries.
        today=g.today.isoformat()  # Sends today's date to the HTML page.
    )


# Opens the journal page.
@bp.route('/journal')
@login_required  # Only logged-in users can access this page.
def journal():
    # Gets the date selected by the user.
    chosen = parse_date(request.args.get('date'))

    # Uses today's date if the selected date is invalid or in the future.
    day = chosen.isoformat() if chosen and chosen <= g.today else g.today.isoformat()

    # Retrieves the saved entry for the selected date and displays it.
    return render_journal(day, database.get_journal_entry(g.user['id'], day))


# Handles the submission of the daily journal form.
@bp.post('/journal')
@login_required  # Only logged-in users can save journal entries.
def journal_save():

    # Gets and checks the date submitted by the user.
    chosen = parse_date(request.form.get('date'))

    # Rejects invalid dates and future dates.
    if chosen is None or chosen > g.today:
        abort(400)

    # Converts the selected date into a string.
    day = chosen.isoformat()

    # Gets the selected mood from the form.
    mood_text = request.form.get('mood', '')

    # Converts study hours into a number.
    try:
        hours = float(request.form.get('hours', 0))
    except ValueError:
        hours = -1  # Uses -1 if the input is not a valid number.

    # Collects all reflection answers into a dictionary.
    entry = {
        'mood': int(mood_text) if mood_text.isdigit() else 0,
        'went_well': form_text('went_well'),
        'improve': form_text('improve'),
        'hours': hours
    }

    # Checks whether the user selected a valid mood (1 to 5).
    if not 1 <= entry['mood'] <= 5:
        return render_journal(day, entry, 'Pick how your day felt first.')

    # Checks whether study hours are between 0 and 10 and are valid numbers.
    if not (0 <= hours <= 10 and math.isfinite(hours)):
        return render_journal(day, entry, 'Study hours must be between 0 and 10.')

    # Checks whether a journal entry already exists for this date.
    is_new = not database.has_journal_entry(g.user['id'], day)

    # Saves the journal entry into the database.
    # Existing entries for the same date will be updated.
    database.save_journal_entry(
        g.user['id'], day, entry['mood'],
        entry['went_well'], entry['improve'], hours
    )

    # Displays a message depending on whether the entry is new or updated.
    flash('Summary saved' if is_new else 'Summary updated')

    # Redirects the user back to the journal page for the saved date.
    return redirect(url_for('journal.journal', date=day))
