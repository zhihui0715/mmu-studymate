"""routes/subjects.py - add, edit, delete and restore subjects.    [OWNER: Tan Yu Zhe]

Pages:  /subjects               the list + Add form   (?edit=<id> opens one for editing)
        /subjects/add           POST: save a new subject
        /subjects/add-mmu       POST: restore one subject from the MMU list
        /subjects/<id>/save     POST: save the edited subject
        /subjects/<id>/delete   POST: delete (its tasks go too)
W4 adds the "N of M tasks done" count once tasks exist.
"""
import re                                        # built-in: checks the colour code

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

import database
from data import MMU_SUBJECTS
from helpers import form_text, login_required, parse_weight

bp = Blueprint('subjects', __name__)


def render_subjects(error='', editing=None, typed=None):
    """Draws the page. `typed` keeps what the user typed after an error."""
    rows = database.list_subjects(g.user['id'])
    have = {s['code'] for s in rows}
    missing = [(code, name) for code, name, _, _, _ in MMU_SUBJECTS if code not in have]   # for the restore list
    return render_template('subjects.html', subjects=rows, error=error, editing=editing,
                           typed=typed or {}, missing=missing)


def read_subject_form():
    """Reads the add/edit form. Returns (fields, error); error is '' when all is fine."""
    fields = {
        'code': form_text('code', 20).upper(), 'name': form_text('name', 80),
        'lecturer': form_text('lecturer', 80) or 'Lecturer',
        'weight': request.form.get('weight', ''), 'color': request.form.get('color', ''),
    }
    weight = parse_weight(fields['weight'])
    if not fields['code'] or not fields['name']:
        return fields, 'Enter a subject code and name.'
    if weight is None:
        return fields, 'Weight must be between 0.1 and 3.'
    if not re.fullmatch(r'#[0-9a-fA-F]{6}', fields['color']):     # e.g. #9BE15D
        return fields, 'Choose a valid colour.'
    fields['weight'] = weight
    return fields, ''


@bp.route('/subjects')
@login_required
def subjects():
    edit_text = request.args.get('edit', '')
    editing = int(edit_text) if edit_text.isdigit() else None
    if editing and not database.get_subject(g.user['id'], editing):
        editing = None                           # not your subject: just show the list
    return render_subjects(editing=editing)


@bp.post('/subjects/add')
@login_required
def subject_add():
    fields, error = read_subject_form()
    if error:
        return render_subjects(error, typed=fields)
    database.add_subject(g.user['id'], fields['code'], fields['name'], fields['lecturer'],
                         fields['weight'], fields['color'])
    flash('Subject added')
    return redirect(url_for('subjects.subjects'))


@bp.post('/subjects/add-mmu')
@login_required
def subject_add_mmu():
    """Restores one subject from the MMU list. Only codes in MMU_SUBJECTS are accepted."""
    code = request.form.get('code', '')
    subject = next((s for s in MMU_SUBJECTS if s[0] == code), None)
    if subject is None:
        abort(400)
    if code in {s['code'] for s in database.list_subjects(g.user['id'])}:
        flash(f'You already have {code}.')
    else:
        database.add_subject(g.user['id'], *subject)
        flash(f'{code} added')
    return redirect(url_for('subjects.subjects'))


@bp.post('/subjects/<int:subject_id>/save')
@login_required
def subject_save(subject_id):
    database.get_subject(g.user['id'], subject_id) or abort(404)   # 404 if not your subject
    fields, error = read_subject_form()
    if error:
        return render_subjects(error, editing=subject_id, typed=fields)
    database.update_subject(g.user['id'], subject_id, fields['code'], fields['name'], fields['lecturer'],
                            fields['weight'], fields['color'])
    flash('Subject saved')
    return redirect(url_for('subjects.subjects'))


@bp.post('/subjects/<int:subject_id>/delete')
@login_required
def subject_delete(subject_id):
    database.delete_subject(g.user['id'], subject_id)
    return redirect(url_for('subjects.subjects'))