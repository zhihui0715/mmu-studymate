"""routes/ - the pages of StudyMate, one file per feature."""
from routes.account import bp as account_bp     # project file: routes/account.py

ALL_BLUEPRINTS = [account_bp]                    # each teammate adds their blueprint here