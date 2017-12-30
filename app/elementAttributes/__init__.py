from flask import Blueprint

elementAttributes = Blueprint("elementAttributes", __name__)

from . import routes
