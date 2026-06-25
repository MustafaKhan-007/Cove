# COVE Website Rebuild — blueprints/wiki/__init__.py — wiki blueprint
from flask import Blueprint

wiki = Blueprint("wiki", __name__)

from . import routes  # noqa: E402,F401
