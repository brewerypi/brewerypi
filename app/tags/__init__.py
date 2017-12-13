from flask import Blueprint

tags = Blueprint("tags", __name__)

from . import views
