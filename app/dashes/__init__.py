from flask import Blueprint

dashes = Blueprint("dashes", __name__)

from . import routes
