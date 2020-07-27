from flask import Blueprint
eventFramesOverlay = Blueprint("eventFramesOverlay", __name__)
from . import routes
