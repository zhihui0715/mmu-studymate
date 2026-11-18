"""routes/ - the pages of StudyMate, one file per feature area. Each member adds their blueprint here."""
from routes.account import bp as account_bp     # Zhi Hui
from routes.journal import bp as journal_bp         # Kong
from routes.subjects import bp as subjects_bp   # Tan

ALL_BLUEPRINTS = [account_bp, subjects_bp, journal_bp]  # Add all blueprints to this list
