from flask import Blueprint

unitOfMeasurements = Blueprint("unitOfMeasurements", __name__)

from . import views
