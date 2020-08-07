from flask import render_template
from . import main

@main.route("/")
def index():
	version = "AWS"
	return render_template("main/index.html", version = version)
