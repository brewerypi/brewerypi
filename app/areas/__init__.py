from flask import Blueprint

areas = Blueprint("areas", __name__)

from . import routes
