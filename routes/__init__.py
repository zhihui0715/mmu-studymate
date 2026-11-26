"""routes/ - the pages of StudyMate, one file per feature area. Each member adds their blueprint here."""
from routes.account import bp as account_bp     # Zhi Hui
from routes.journal import bp as journal_bp     # Kong
from routes.subjects import bp as subjects_bp   # Tan
from routes.dashboard import bp as dashboard_bp # Kong (W3)
from routes.tasks import bp as tasks_bp         # Tan (W3)

ALL_BLUEPRINTS = [account_bp, dashboard_bp, subjects_bp, tasks_bp, journal_bp]
