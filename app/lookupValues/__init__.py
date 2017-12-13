from flask import Blueprint

lookupValues = Blueprint("lookupValues", __name__)

from . import views
