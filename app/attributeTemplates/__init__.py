from flask import Blueprint

attributeTemplates = Blueprint("attributeTemplates", __name__)

from . import routes
