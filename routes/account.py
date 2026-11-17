"""routes/account.py - sign up, log in, log out."""
import sqlite3                                   # built-in: needed to catch IntegrityError

from flask import Blueprint, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
# werkzeug = third-party (comes with Flask): password hashing (one-way scramble 单向加密)

import database                                  # project file
from helpers import form_text, is_valid_email    # project file

bp = Blueprint('account', __name__)              # a group of routes; page names start with 'account.'


@bp.route('/')
def home():
    # TODO: when Kong's dashboard is merged, send logged-in users to url_for('dashboard.dashboard')
    return render_template('landing.html')


@bp.route('/login', methods=['GET', 'POST'])     # GET = show the form, POST = form was submitted
def login():
    if g.user:                                   # already logged in
        return redirect(url_for('account.home'))  # TODO: dashboard later
    error, email = '', ''
    if request.method == 'POST':
        email = form_text('email', 254).lower()   # lower(): Zhi@x.com and zhi@x.com are the same
        password = request.form.get('password', '')  # not stripped: spaces can be part of a password
        if not is_valid_email(email):
            error = 'Enter a valid email, for example name@gmail.com.'
        elif not password:
            error = 'Enter your password.'
        else:
            account = database.get_user_by_email(email)
            if account and check_password_hash(account['password_hash'], password):
                session.clear()                   # fresh session for this user
                session['uid'] = account['id']    # this browser is now logged in
                return redirect(url_for('account.home'))  # TODO: dashboard later
            error = 'Wrong email or password.'    # same message for both cases: hides which emails exist
    return render_template('login.html', error=error, email=email)


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if g.user:
        return redirect(url_for('account.home'))  # TODO: dashboard later
    error, name, email = '', '', ''
    if request.method == 'POST':
        name = form_text('name', 60)
        email = form_text('email', 254).lower()
        password = request.form.get('password', '')
        # The first problem found becomes the error message.
        if not name:
            error = 'Please enter your name.'
        elif not is_valid_email(email):
            error = 'Enter a valid email, for example name@gmail.com.'
        elif not 8 <= len(password) <= 128:
            error = 'Use 8 to 128 characters for your password.'
        elif password != request.form.get('password2', ''):
            error = 'The two passwords do not match.'
        elif database.get_user_by_email(email):
            error = 'An account with this email already exists.'
        else:
            try:
                user_id = database.create_user(name, email, generate_password_hash(password))
            except sqlite3.IntegrityError:        # same email signed up at the same moment (UNIQUE rule)
                error = 'An account with this email already exists.'
            else:                                 # no error: log the new user in
                session.clear()
                session['uid'] = user_id
                return redirect(url_for('account.home'))  # TODO: dashboard later
    return render_template('signup.html', error=error, name=name, email=email)  # keep typed values


@bp.post('/logout')                               # POST only: a link or image can't log you out
def logout():
    session.clear()                               # forget the login
    return redirect(url_for('account.home'))