from flask import Blueprint

physicalModels = Blueprint("physicalModels", __name__)

from . import routes
