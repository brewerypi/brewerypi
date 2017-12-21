from flask import Blueprint

lookups = Blueprint("lookups", __name__)

from . import routes
