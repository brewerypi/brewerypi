# app/dataEntry/__init__.py

from flask import Blueprint

dataEntry = Blueprint('dataEntry', __name__)

from . import views
