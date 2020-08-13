from flask import render_template
from app import __version__
from . import main

@main.route("/")
def index():
	version = __version__
	return render_template("main/index.html", version = version)
