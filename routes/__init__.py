"""routes/ - the pages of StudyMate, one file per feature area. Each member adds their blueprint here."""
from routes.account import bp as account_bp     # Zhi Hui
from routes.study import bp as study_bp         # Kong
from routes.subjects import bp as subjects_bp   # Tan

ALL_BLUEPRINTS = [account_bp, subjects_bp, study_bp]
