"""routes/account.py - welcome page, sign up, log in, log out, profile.     [OWNER: Zhi Hui]

W2: welcome, sign up, log in, log out.
W3: /profile (edit name, email, course, semester) and change password.
Passwords are never stored: generate_password_hash() makes a one-way hash (单向加密).
"""
import sqlite3                                   # built-in: to catch IntegrityError

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

import database
from helpers import form_text, is_valid_email, login_required

bp = Blueprint('account', __name__)              # page names start with 'account.'

AFTER_LOGIN = 'dashboard.dashboard'              # W3 (Kong): login now goes to his dashboard
SEMESTERS = ('Semester 1', 'Semester 2', 'Semester 3')


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


# ---------- W3: profile and password ----------

def render_profile(profile_error='', password_error='', values=None):
    """`values` = what the student typed, shown again after an error (default: the saved profile)."""
    return render_template('profile.html', profile_error=profile_error, password_error=password_error,
                           values=values or g.user, semesters=SEMESTERS)


@bp.route('/profile')
@login_required
def profile():
    return render_profile()


@bp.post('/profile')
@login_required
def profile_save():
    name, course = form_text('name', 60), form_text('course', 120)
    email, semester = form_text('email', 254).lower(), request.form.get('semester', '')
    typed = {'name': name, 'email': email, 'course': course, 'semester': semester}
    other = database.get_user_by_email(email)    # someone else with this email?

    if not name:
        return render_profile(profile_error='Please enter your name.', values=typed)
    if not is_valid_email(email):
        return render_profile(profile_error='Enter a valid email address.', values=typed)
    if not course:
        return render_profile(profile_error='Please enter your course.', values=typed)
    if semester not in SEMESTERS:                 # only the 3 allowed values are saved
        return render_profile(profile_error='Choose a semester.', values=typed)
    if other and other['id'] != g.user['id']:
        return render_profile(profile_error='Another account already uses this email.', values=typed)

    try:
        database.update_profile(g.user['id'], name, email, course, semester)
    except sqlite3.IntegrityError:                # same email saved by someone at the same moment
        return render_profile(profile_error='Another account already uses this email.', values=typed)
    flash('Profile saved')
    return redirect(url_for('account.profile'))   # redirect after POST: refresh will not resend the form


@bp.post('/profile/password')
@login_required
def password_save():
    new_password = request.form.get('new', '')
    # The current password must be right first, so a borrowed logged-in laptop cannot change it
    if not check_password_hash(g.user['password_hash'], request.form.get('current', '')):
        return render_profile(password_error='Current password is incorrect.')
    if not 8 <= len(new_password) <= 128:
        return render_profile(password_error='Use 8 to 128 characters for the new password.')
    if new_password != request.form.get('new2', ''):
        return render_profile(password_error='The two new passwords do not match.')

    database.set_password_hash(g.user['id'], generate_password_hash(new_password))
    flash('Password updated')
    return redirect(url_for('account.profile'))
