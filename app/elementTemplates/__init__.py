from flask import Blueprint

elementTemplates = Blueprint("elementTemplates", __name__)

from . import routes
