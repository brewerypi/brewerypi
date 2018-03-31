from flask import Blueprint

raspberryPiUtilities = Blueprint("raspberryPiUtilities", __name__)

from . import routes
