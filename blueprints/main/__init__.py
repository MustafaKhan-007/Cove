# COVE Website Rebuild — blueprints/main/__init__.py — main blueprint
from flask import Blueprint

main = Blueprint("main", __name__)

from . import routes  # noqa: E402,F401
