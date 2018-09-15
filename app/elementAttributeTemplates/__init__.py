from flask import Blueprint

elementAttributeTemplates = Blueprint("elementAttributeTemplates", __name__)

from . import routes
