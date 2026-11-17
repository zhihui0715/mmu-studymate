"""helpers.py - small tools that the route files share."""
import re                                   # built-in: regular expressions (pattern matching)
from functools import wraps                 # built-in: keeps a function's name when wrapping it

from flask import g, redirect, request, url_for
# g        = this request's storage (app.py puts the logged-in user in g.user)
# redirect = sends the browser to another page
# request  = the incoming request (form data, etc.)
# url_for  = builds a URL from a route name, e.g. url_for('account.login') -> /login


# ---------- login check ----------

def login_required(view):
    """Put @login_required above a route to make it members-only."""
    @wraps(view)                            # keeps the original function name (Flask needs it)
    def wrapped(*args, **kwargs):           # *args, **kwargs = pass along any arguments
        if g.user is None:                  # nobody logged in
            return redirect(url_for('account.login'))
        return view(*args, **kwargs)        # logged in: run the real page
    return wrapped
# This is a decorator (装饰器): a function that wraps another function to add a check before it.


# ---------- reading and checking form input ----------

def is_valid_email(email):
    """something@something.something, at most 254 characters."""
    return bool(re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email)) and len(email) <= 254
    # [^\s@]+  = one or more characters that are not a space or @
    # fullmatch = the WHOLE text must fit the pattern, not just part of it
    # 254 = the longest email address the standard allows


def form_text(name, limit=500):
    """One text box from the form: spaces trimmed, cut to `limit` characters."""
    return (request.form.get(name) or '').strip()[:limit]
    # .get(name) or ''  = empty text if the box is missing (avoids a crash on None)
    # .strip()          = removes spaces at the start and end
    # [:limit]          = cuts off anything too long, so nobody can save a huge text