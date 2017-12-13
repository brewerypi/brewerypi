from flask import Blueprint

elements = Blueprint("elements", __name__)

from . import views
