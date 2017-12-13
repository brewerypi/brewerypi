from flask import Blueprint

tagValues = Blueprint("tagValues", __name__)

from . import views
