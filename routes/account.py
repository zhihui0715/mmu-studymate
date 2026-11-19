"""routes/account.py - welcome page, sign up, log in, log out.     [OWNER: Zhi Hui]

After login users go to the Subjects page until Kong's dashboard exists (W3).
Passwords are never stored: generate_password_hash() makes a one-way hash (单向加密).
"""
import sqlite3                                   # built-in: to catch IntegrityError

from flask import Blueprint, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

import database
from helpers import form_text, is_valid_email

bp = Blueprint('account', __name__)              # page names start with 'account.'

AFTER_LOGIN = 'subjects.subjects'                # TODO W3: change to 'dashboard.dashboard'


@bp.route('/')
def home():
    if g.user:
        return redirect(url_for(AFTER_LOGIN))
    return render_template('landing.html')


@bp.route('/login', methods=['GET', 'POST'])     # GET = show form, POST = form submitted
def login():
    if g.user:
        return redirect(url_for(AFTER_LOGIN))
    error, email = '', ''
    if request.method == 'POST':
        email = form_text('email', 254).lower()
        password = request.form.get('password', '')
        if not is_valid_email(email):
            error = 'Enter a valid email, for example name@gmail.com.'
        elif not password:
            error = 'Enter your password.'
        else:
            account = database.get_user_by_email(email)
            if account and check_password_hash(account['password_hash'], password):
                session.clear()
                session['uid'] = account['id']   # this browser is now logged in
                return redirect(url_for(AFTER_LOGIN))
            error = 'Wrong email or password.'    # same message: hides which emails exist
    return render_template('login.html', error=error, email=email)


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if g.user:
        return redirect(url_for(AFTER_LOGIN))
    error, name, email = '', '', ''
    if request.method == 'POST':
        name = form_text('name', 60)
        email = form_text('email', 254).lower()
        password = request.form.get('password', '')
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
            except sqlite3.IntegrityError:        # same email at the same moment (UNIQUE)
                error = 'An account with this email already exists.'
            else:
                session.clear()
                session['uid'] = user_id
                return redirect(url_for(AFTER_LOGIN))
    return render_template('signup.html', error=error, name=name, email=email)


@bp.post('/logout')                               # POST only: a link can't log you out
def logout():
    session.clear()
    return redirect(url_for('account.home'))
