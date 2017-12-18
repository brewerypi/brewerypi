from flask import Blueprint

eventFrames = Blueprint("eventFrames", __name__)

from . import views
