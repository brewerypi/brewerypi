from flask import Blueprint

eventFrameGroups = Blueprint("eventFrameGroups", __name__)

from . import routes
