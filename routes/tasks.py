"""routes/tasks.py - add, edit and delete tasks.                [OWNER: Tan Yu Zhe]

Pages:  /tasks                  the task list (earliest due date first)
        /tasks?new=1            the list with an empty "add task" form
        /tasks?edit=<id>        the list with one task open for editing
        /tasks/save             POST: save a new or edited task
        /tasks/<id>/delete      POST: delete a task
W3: a plain list. W4 turns it into the kanban board (To do / In progress / Completed),
W5 adds search and filters.
"""
from datetime import timedelta                   # built-in: "3 days from today"

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

import database
from data import PRIORITIES, TASK_TYPES
from helpers import MAX_EST_HOURS, form_text, login_required, parse_date, parse_hours, redirect_back

bp = Blueprint('tasks', __name__)                # page names start with 'tasks.'


def render_tasks(editing=None, form_task=None, error=''):
    """Draws the page. `editing` is None, 'new', or the id of the task being edited."""
    user_id = g.user['id']
    subjects = database.list_subjects(user_id)
    if editing and form_task is None:
        if editing == 'new':
            # sensible defaults: first subject, Medium priority, due in 3 days
            form_task = {'name': '', 'description': '', 'type': 'Assignment', 'priority': 'Medium',
                         'subject_id': subjects[0]['id'] if subjects else 0,
                         'due': (g.today + timedelta(days=3)).isoformat(), 'est_hours': 0}
        else:
            form_task = database.get_task(user_id, editing)
    return render_template(
        'tasks.html', tasks=database.list_tasks(user_id), subjects=subjects, task_types=TASK_TYPES,
        priorities=PRIORITIES, editing=editing, form_task=form_task, error=error, max_hours=MAX_EST_HOURS,
    )


@bp.route('/tasks')
@login_required
def tasks():
    editing = None
    if request.args.get('new'):
        editing = 'new'
    elif request.args.get('edit', '').isdigit():
        editing = int(request.args['edit'])
        if not database.get_task(g.user['id'], editing):
            editing = None                       # not your task (or deleted): just show the list
    return render_tasks(editing)


@bp.post('/tasks/save')
@login_required
def task_save():
    """Adds a new task, or saves changes when the form carries a task id."""
    user_id = g.user['id']
    task_id = request.form.get('id', '')
    editing = int(task_id) if task_id.isdigit() else 'new'
    if editing != 'new' and not database.get_task(user_id, editing):
        abort(404)                               # someone else's task id

    subject_text = request.form.get('subject_id', '')
    fields = {
        'name': form_text('name', 120), 'description': form_text('description', 500),
        'type': request.form.get('type', ''), 'priority': request.form.get('priority', ''),
        'due': form_text('due', 10),
        'subject_id': int(subject_text) if subject_text.isdigit() else 0,
    }
    est_text = form_text('est_hours', 10)
    est_hours = parse_hours(est_text)
    fields['est_hours'] = est_text if est_hours is None else est_hours   # typed text is shown again on an error

    # One check per field. The lists TASK_TYPES and PRIORITIES make sure only allowed values are saved.
    error = ''
    if not fields['name']:
        error = 'Give the task a name.'
    elif parse_date(fields['due']) is None:
        error = 'Choose a valid due date.'
    elif not database.list_subjects(user_id):
        error = 'Add a subject first.'
    elif not database.get_subject(user_id, fields['subject_id']):
        error = 'Choose one of your subjects.'
    elif fields['type'] not in TASK_TYPES:
        error = 'Choose a task type from the list.'
    elif fields['priority'] not in PRIORITIES:
        error = 'Choose a priority from the list.'
    elif est_hours is None:
        error = f'Estimated study time must be a number from 0 to {MAX_EST_HOURS} hours.'
    if error:
        return render_tasks(editing, form_task=fields, error=error)

    if editing == 'new':
        database.add_task(user_id, fields)
        flash('Task added')
    else:
        database.update_task(user_id, editing, fields)
        flash('Task saved')
    return redirect(url_for('tasks.tasks'))


@bp.post('/tasks/<int:task_id>/delete')
@login_required
def task_delete(task_id):
    database.delete_task(g.user['id'], task_id)  # AND user_id = ? inside: only your own
    flash('Task deleted')
    return redirect_back('tasks.tasks')          # back to the list (W4 forms send a 'next' address)
