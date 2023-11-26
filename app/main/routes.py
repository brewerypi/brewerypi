from flask import render_template
from flask_login import current_user
from app import __version__
from app.main import main
from app.models import Enterprise, EventFrameGroup

@main.route("/")
def index():
	version = __version__
	if current_user.is_authenticated:
		enterprises = Enterprise.query.all()
		eventFrameGroups = EventFrameGroup.query.all()
	else:
		enterprises = None
		eventFrameGroups = None

	return render_template("main/index.html", enterprises = enterprises, eventFrameGroups = eventFrameGroups, version = version)
