from flask import Blueprint

eventFrameNotes = Blueprint("eventFrameNotes", __name__)

from . import routes
