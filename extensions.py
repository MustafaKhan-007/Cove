# COVE Website Rebuild — extensions.py — shared Flask extension singletons
from flask_sqlalchemy import SQLAlchemy

try:
    from flask_mail import Mail
    mail = Mail()
    HAS_MAIL = True
except Exception:  # noqa: BLE001 — Flask-Mail optional in some envs
    mail = None
    HAS_MAIL = False

db = SQLAlchemy()
