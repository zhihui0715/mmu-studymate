"""app.py - the starting point of StudyMate (Flask + SQLite).

Run:   flask run --debug
Open:  http://127.0.0.1:5000
"""
import os                                   # built-in: file paths + environment variables
from flask import Flask, g, session         # third-party: app, per-request storage, login cookie

import database                             # project file: database.py
from routes import ALL_BLUEPRINTS           # project file: routes/__init__.py


# ---------- 1. the app and its settings ----------

HERE = os.path.dirname(os.path.abspath(__file__))   # full path of the project folder

app = Flask(__name__, instance_path=os.path.join(HERE, 'instance'))
# __name__ helps Flask find templates/ and static/
# instance/ holds the database (not pushed to GitHub)

app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-only-change-me'),  # signs the login cookie (签名) so it can't be faked
    DATABASE=os.path.join(app.instance_path, 'studymate.db'),       # full path to the SQLite file
    SESSION_COOKIE_SAMESITE='Lax',                                  # blocks cross-site form attacks (CSRF 跨站请求伪造)
)


# ---------- 2. the database ----------

database.init_app(app)                      # creates instance/studymate.db and its tables if missing


# ---------- 3. the pages ----------

for blueprint in ALL_BLUEPRINTS:
    app.register_blueprint(blueprint)       # plug each feature's routes into the app


# ---------- 4. load the logged-in user before every request ----------

@app.before_request                         # runs before EVERY page
def load_user():
    g.user = None                           # default: nobody logged in
    user_id = session.get('uid')            # the id saved at login, or None
    if user_id:
        user = database.get_user(user_id)
        if user is None:                    # account was deleted: forget the old login
            session.clear()
        else:
            g.user = user                   # every route and template can now use g.user

@app.context_processor                      # values every template can use
def inject_globals():
    return {'user': g.get('user')}          # base.html checks "user" to pick logged-in or logged-out layout


# ---------- start the server (always last) ----------

if __name__ == '__main__':                  # only runs with "python app.py"
    app.run(debug=True)                     # auto-restart + error pages (never on a public server)