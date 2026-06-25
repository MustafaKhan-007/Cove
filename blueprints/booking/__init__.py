# COVE Website Rebuild — blueprints/booking/__init__.py — booking blueprint
from flask import Blueprint

booking = Blueprint("booking", __name__)

from . import routes  # noqa: E402,F401
