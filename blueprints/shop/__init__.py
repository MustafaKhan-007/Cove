# COVE Website Rebuild — blueprints/shop/__init__.py — shop blueprint
from flask import Blueprint

shop = Blueprint("shop", __name__)

from . import routes  # noqa: E402,F401
