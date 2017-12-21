from flask import Blueprint

eventFrameTemplates = Blueprint("eventFrameTemplates", __name__)

from . import routes
