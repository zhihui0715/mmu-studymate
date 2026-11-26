"""database.py - everything that touches SQLite.

Shared file: each member edits ONLY their own marked section.
Safety rules: every query has "WHERE ... user_id = ?" and every value goes in through a ? placeholder.
Changed a table? Delete instance/studymate.db and run the app again.
"""
import sqlite3                              # built-in: talks to SQLite
from pathlib import Path                    # built-in: folders and files

import click                                # third-party (comes with Flask): terminal commands
from flask import current_app, g            # current_app = running app, g = storage for one request

from data import DEFAULT_SUBJECTS           # project file (Tan)


# ---------- the tables ----------
SCHEMA = """
-- ===== [OWNER: Zhi Hui] users =====
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY,
    name            TEXT NOT NULL,
    email           TEXT NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL,                        -- never the real password
    course          TEXT NOT NULL DEFAULT 'Foundation in Computing and Informatics',
    semester        TEXT NOT NULL DEFAULT 'Semester 1'
);

-- ===== [OWNER: Tan Yu Zhe] subjects and tasks =====
CREATE TABLE IF NOT EXISTS subjects (
    id        INTEGER PRIMARY KEY,
    user_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    code      TEXT NOT NULL,
    name      TEXT NOT NULL,
    lecturer  TEXT NOT NULL DEFAULT 'Lecturer',
    weight    REAL NOT NULL DEFAULT 1,                      -- used by Kong's workload score
    color     TEXT NOT NULL DEFAULT '#9BE15D'
);

CREATE TABLE IF NOT EXISTS tasks (
    id           INTEGER PRIMARY KEY,
    user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject_id   INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    name         TEXT NOT NULL,
    description  TEXT NOT NULL DEFAULT '',
    type         TEXT NOT NULL,
    due          TEXT NOT NULL,                             -- e.g. 2026-12-05
    priority     TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'todo' CHECK (status IN ('todo', 'prog', 'done')),
    finished_on  TEXT NOT NULL DEFAULT '',
    xp_given     INTEGER NOT NULL DEFAULT 0,
    est_hours    REAL NOT NULL DEFAULT 0 CHECK (est_hours >= 0)   -- read by Kong's planner
);

-- ===== [OWNER: Kong Fu Sheng] journal =====
CREATE TABLE IF NOT EXISTS journal (
    user_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    day       TEXT NOT NULL,
    mood      INTEGER NOT NULL CHECK (mood BETWEEN 1 AND 5),
    went_well TEXT NOT NULL DEFAULT '',
    improve   TEXT NOT NULL DEFAULT '',
    hours     REAL NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, day)                              -- one entry per user per day
);
"""


# ---------- [OWNER: Zhi Hui] set-up ----------

def get_db():
    """One connection per request, opened on first use."""
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row                     # rows act like dicts: row['email']
        g.db.execute('PRAGMA foreign_keys = ON')           # needed for ON DELETE CASCADE and foreign key checks
    return g.db


def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    get_db().executescript(SCHEMA)


def init_app(app):
    """Called once from app.py: makes instance/, the tables, and `flask init-db`."""
    Path(app.config['DATABASE']).parent.mkdir(parents=True, exist_ok=True) # instance/ folder
    app.teardown_appcontext(close_db) 

    with app.app_context():
        init_db()

    @app.cli.command('init-db') # terminal: flask init-db
    def init_db_command():
        init_db()
        click.echo('Database ready.')


def _one(sql, params=()): # params = tuple of values for the ? placeholders
    """First row as a dict, or None."""
    row = get_db().execute(sql, params).fetchone()
    return dict(row) if row else None # conditional expression: dict(row) if row else None


def _all(sql, params=()):
    """Every row as a list of dicts."""
    return [dict(row) for row in get_db().execute(sql, params).fetchall()] # list comprehension


# ---------- [OWNER: Zhi Hui] users ----------

def create_user(name, email, password_hash):
    """Saves a new account (plus its default subjects). Returns the new user id."""
    db = get_db()
    cursor = db.execute(
        'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)', (name, email, password_hash)
    )
    user_id = cursor.lastrowid # the new user's id, used to add the default subjects
    db.executemany(
        'INSERT INTO subjects (user_id, code, name, lecturer, weight, color) VALUES (?, ?, ?, ?, ?, ?)',
        [(user_id, *subject) for subject in DEFAULT_SUBJECTS],
    )
    db.commit()
    return user_id


def get_user(user_id):
    return _one('SELECT * FROM users WHERE id = ?', (user_id,))


def get_user_by_email(email):
    return _one('SELECT * FROM users WHERE email = ?', (email,))


# ---------- [OWNER: Tan Yu Zhe] tasks W3 ----------

# Every task comes back with its subject's code, colour and weight (JOIN), so pages
# and Kong's task_score() do not need a second query.
_TASK_SELECT = """
    SELECT t.*, s.code AS subject_code, s.color AS subject_color, s.weight AS subject_weight
    FROM tasks t JOIN subjects s ON s.id = t.subject_id
"""


def list_tasks(user_id):
    return _all(_TASK_SELECT + ' WHERE t.user_id = ? ORDER BY t.due, t.id', (user_id,))


def get_task(user_id, task_id):
    return _one(_TASK_SELECT + ' WHERE t.id = ? AND t.user_id = ?', (task_id, user_id))


def add_task(user_id, fields):
    """Saves a new task and returns its id."""
    db = get_db()
    cursor = db.execute(
        'INSERT INTO tasks (user_id, subject_id, name, description, type, due, priority, est_hours) '
        'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (user_id, fields['subject_id'], fields['name'], fields['description'],
         fields['type'], fields['due'], fields['priority'], fields['est_hours']),
    )
    db.commit()
    return cursor.lastrowid


def update_task(user_id, task_id, fields):
    """AND user_id = ? means you can only edit your own tasks."""
    db = get_db()
    db.execute(
        'UPDATE tasks SET subject_id = ?, name = ?, description = ?, type = ?, due = ?, priority = ?, '
        'est_hours = ? WHERE id = ? AND user_id = ?',
        (fields['subject_id'], fields['name'], fields['description'], fields['type'],
         fields['due'], fields['priority'], fields['est_hours'], task_id, user_id),
    )
    db.commit()


def delete_task(user_id, task_id):
    db = get_db()
    db.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?', (task_id, user_id))
    db.commit()

# ---------- [OWNER: Tan Yu Zhe] subjects ----------

def list_subjects(user_id):
    return _all('SELECT * FROM subjects WHERE user_id = ? ORDER BY id', (user_id,)) #_all() returns a list of dicts, each dict = one row


def get_subject(user_id, subject_id):
    return _one('SELECT * FROM subjects WHERE id = ? AND user_id = ?', (subject_id, user_id))


def add_subject(user_id, code, name, lecturer, weight, color):
    db = get_db()
    db.execute(
        'INSERT INTO subjects (user_id, code, name, lecturer, weight, color) VALUES (?, ?, ?, ?, ?, ?)',
        (user_id, code, name, lecturer, weight, color),
    )
    db.commit()


def update_subject(user_id, subject_id, code, name, lecturer, weight, color):
    """AND user_id = ? means you can only edit your own subjects."""
    db = get_db()
    db.execute(
        'UPDATE subjects SET code = ?, name = ?, lecturer = ?, weight = ?, color = ? WHERE id = ? AND user_id = ?',
        (code, name, lecturer, weight, color, subject_id, user_id),
    )
    db.commit()


def delete_subject(user_id, subject_id):
    """Also deletes the subject's tasks (ON DELETE CASCADE)."""
    db = get_db()
    db.execute('DELETE FROM subjects WHERE id = ? AND user_id = ?', (subject_id, user_id))
    db.commit()


# ---------- [OWNER: Kong Fu Sheng] journal ----------

def get_journal_entry(user_id, day):
    return _one('SELECT * FROM journal WHERE user_id = ? AND day = ?', (user_id, day))


def recent_journal(user_id, limit=7):
    return _all('SELECT * FROM journal WHERE user_id = ? ORDER BY day DESC LIMIT ?', (user_id, limit))


def has_journal_entry(user_id, day):
    return get_journal_entry(user_id, day) is not None


def save_journal_entry(user_id, day, mood, went_well, improve, hours):
    """Adds the day's entry, or UPDATES it if that day already has one (ON CONFLICT)."""
    db = get_db()
    db.execute(
        'INSERT INTO journal (user_id, day, mood, went_well, improve, hours) VALUES (?, ?, ?, ?, ?, ?) '
        'ON CONFLICT(user_id, day) DO UPDATE SET mood = excluded.mood, went_well = excluded.went_well, '
        'improve = excluded.improve, hours = excluded.hours', # upsert: add or update if already exists
        (user_id, day, mood, went_well, improve, hours),
    )
    db.commit()