import os

from flask import Flask

# ---------- 1. the app and its settings ----------
HERE = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, instance_path=os.path.join(HERE, 'instance'))
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-only-change-me'),
    DATABASE=os.path.join(app.instance_path, 'studymate.db'),
    SESSION_COOKIE_SAMESITE='Lax',
)


@app.route('/')
def home():
    return 'StudyMate is running'   # temporary, replaced by the landing page later


if __name__ == '__main__':
    app.run(debug=True)