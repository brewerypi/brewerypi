from flask import Blueprint

eventFrameTemplateViews = Blueprint("eventFrameTemplateViews", __name__)

from . import routes
