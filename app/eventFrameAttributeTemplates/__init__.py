from flask import Blueprint

eventFrameAttributeTemplates = Blueprint("eventFrameAttributeTemplates", __name__)

from . import routes
