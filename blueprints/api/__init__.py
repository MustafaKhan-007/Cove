# COVE Website Rebuild — blueprints/api/__init__.py — JSON API blueprint
from flask import Blueprint

api = Blueprint("api", __name__)

from . import routes  # noqa: E402,F401
