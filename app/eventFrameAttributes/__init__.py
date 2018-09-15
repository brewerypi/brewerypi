from flask import Blueprint

eventFrameAttributes = Blueprint("eventFrameAttributes", __name__)

from . import routes
