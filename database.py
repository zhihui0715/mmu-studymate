"""database.py - everything that touches SQLite (the database)."""
import sqlite3                      # built-in: talks to SQLite
from pathlib import Path            # built-in: works with folders and files

import click                        # third-party (comes with Flask): makes terminal commands
from flask import current_app, g    # current_app = the running app, g = storage for one request


# ---------- the tables ----------
# IF NOT EXISTS: only creates missing tables, so running it again is safe.
SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY,
    name            TEXT NOT NULL,
    email           TEXT NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL,
    course          TEXT NOT NULL DEFAULT 'Foundation in Computing and Informatics',
    semester        TEXT NOT NULL DEFAULT 'Semester 1'
);
"""


# ---------- set-up: opening the database ----------

def get_db():
    """One connection per request, opened on first use."""
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])   # path from app.py
        g.db.row_factory = sqlite3.Row                           # rows act like dicts: row['email']
        g.db.execute('PRAGMA foreign_keys = ON')                 # SQLite ignores foreign keys unless asked
    return g.db


def close_db(error=None):
    """Closes the connection when the request ends."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Creates any missing tables."""
    db = get_db()
    db.executescript(SCHEMA)                # runs all the SQL in SCHEMA


def init_app(app):
    """Called once from app.py: makes the instance folder, the tables, and `flask init-db`."""
    Path(app.config['DATABASE']).parent.mkdir(parents=True, exist_ok=True)  # creates instance/
    app.teardown_appcontext(close_db)       # close the connection after every request

    with app.app_context():                 # get_db() needs a running app
        init_db()

    @app.cli.command('init-db')             # adds the terminal command: flask init-db
    def init_db_command():
        init_db()
        click.echo('Database ready.')


# Shortcuts: _one() = first row as a dict (or None), _all() = every row as a list of dicts.

def _one(sql, params=()):
    row = get_db().execute(sql, params).fetchone()
    return dict(row) if row else None


def _all(sql, params=()):
    return [dict(row) for row in get_db().execute(sql, params).fetchall()]


# ---------- users ----------
# Every value goes in through ? placeholders, never string gluing: this blocks SQL injection.

def create_user(name, email, password_hash):
    """Saves a new account. Returns the new user id."""
    db = get_db()
    cursor = db.execute(
        'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)', (name, email, password_hash)
    )
    db.commit()                             # save the change to the file
    return cursor.lastrowid                 # the id SQLite gave the new row


def get_user(user_id):
    return _one('SELECT * FROM users WHERE id = ?', (user_id,))


def get_user_by_email(email):
    return _one('SELECT * FROM users WHERE email = ?', (email,))


def update_profile(user_id, name, email, course, semester):
    db = get_db()
    db.execute(
        'UPDATE users SET name = ?, email = ?, course = ?, semester = ? WHERE id = ?',
        (name, email, course, semester, user_id),
    )
    db.commit()


def set_password_hash(user_id, password_hash):
    db = get_db()
    db.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, user_id))
    db.commit()