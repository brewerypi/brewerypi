from flask import Blueprint

builders = Blueprint("builders", __name__)

from . import routes
