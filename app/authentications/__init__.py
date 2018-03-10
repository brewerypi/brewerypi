from flask import Blueprint

authentications = Blueprint("authentications", __name__)

from . import routes
