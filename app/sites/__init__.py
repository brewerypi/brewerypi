from flask import Blueprint

sites = Blueprint("sites", __name__)

from . import views
