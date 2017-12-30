from flask import render_template
# from flask_login import login_required
from . import home
from . forms import DefaultForm

@home.route("/")
def homepage():
	return render_template("home/index.html")

# @home.route("/dashboard")
# @login_required
# def dashboard():
# 	return render_template("home/dashboard.html", title = "Dashboard")

@home.route("/defaults")
def defaults():
	form = DefaultForm()
	return render_template("home/defaults.html", form = form)

