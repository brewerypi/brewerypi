from flask import Blueprint

customTemplateFilters = Blueprint("customTemplateFilters", __name__)

from . import filters
