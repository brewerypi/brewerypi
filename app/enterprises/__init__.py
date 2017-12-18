from flask import Blueprint

enterprises = Blueprint("enterprises", __name__)

from . import views
