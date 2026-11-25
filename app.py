"""app.py - the starting point of StudyMate.                [OWNER: Zhi Hui]

W2: sections 1-3, load_user() with g.today and g.user only, inject_globals() with user and nav_tabs.
Run:  python -m flask run --debug
"""
import os                                   # built-in: file paths + environment variables
from datetime import date                   # built-in: today's date

from flask import Flask, g, session         # third-party: app, per-request storage, login cookie 


import database                             # project file
from routes import ALL_BLUEPRINTS           # project file


# ---------- 1. the app and its settings ----------

HERE = os.path.dirname(os.path.abspath(__file__))   # full path of the project folder

app = Flask(__name__, instance_path=os.path.join(HERE, 'instance'))   # instance/ holds the database

app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-only-change-me'),  # signs the login cookie 
    DATABASE=os.path.join(app.instance_path, 'studymate.db'),       # full path to the SQLite file
    SESSION_COOKIE_SAMESITE='Lax',                                  # blocks cross-site form attacks (CSRF)
)


# ---------- 2. the database ----------

database.init_app(app)                      # creates instance/studymate.db and all tables if missing


# ---------- 3. the pages ----------

for blueprint in ALL_BLUEPRINTS:
    app.register_blueprint(blueprint)       # plug each member's routes into the app

# Left menu: (page name, label). Add a line only when the page exists.
NAV_TABS = [
    ('dashboard.dashboard', 'Dashboard'),   # Kong (W3)
    ('tasks.tasks', 'Tasks'),               # Tan (W3)
    ('subjects.subjects', 'Subjects'),      # Tan
    ('journal.journal', 'Journal'),         # Kong
    ('account.profile', 'Profile'),         # Zhi Hui (W3)
]


# ---------- 4. before every request ----------

@app.before_request                         # runs before EVERY page
def load_user():
    g.today = date.today()
    g.user = None                           # default: nobody logged in
    user_id = session.get('uid')            
    if user_id:
        user = database.get_user(user_id)
        if user is None:                    # account was deleted: forget the old login
            session.clear()
        else:
            g.user = user


@app.context_processor                      # return ditcs to every template (HTML page)
def inject_globals():
    return {'user': g.get('user'), 'nav_tabs': NAV_TABS}


# ---------- start the server (always last) ----------

if __name__ == '__main__':
    app.run(debug=True)
