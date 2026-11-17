"""app.py - the starting point of StudyMate (Flask + SQLite)."""
import os                   # built-in: file paths + environment variables
from flask import Flask     # third-party: creates the web app
import database             # project file: our database.py

# ---------- 1. the app and its settings ----------

HERE = os.path.dirname(os.path.abspath(__file__))   # full path of the project folder

app = Flask(__name__, instance_path=os.path.join(HERE, 'instance'))
# __name__ helps Flask find templates/ and static/
# instance/ holds the database (not pushed to GitHub)

app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-only-change-me'),  # signs the login cookie so it can't be faked
    DATABASE=os.path.join(app.instance_path, 'studymate.db'),       # full path to the SQLite file
    SESSION_COOKIE_SAMESITE='Lax',                                  # blocks cross-site form attacks (CSRF attacks)
)


# ---------- temporary test page ----------

@app.route('/')                     # runs when you open "/"
def home():
    return 'StudyMate is running'   # removed later when the real landing page is added


if __name__ == '__main__':          # only runs with "python app.py"
    app.run(debug=True)             # auto-restart + error pages (never on a public server)
