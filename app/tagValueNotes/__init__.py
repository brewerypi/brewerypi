from flask import Blueprint

tagValueNotes = Blueprint("tagValueNotes", __name__)

from . import routes
