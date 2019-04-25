from flask import Blueprint

messages = Blueprint("messages", __name__)

from . import routes
