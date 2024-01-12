from flask import Blueprint
dashes = Blueprint("dashes", __name__)
from app.dashes import routes
