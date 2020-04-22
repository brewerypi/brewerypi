from flask import Blueprint

dash = Blueprint("dash", __name__)

from . import routes
