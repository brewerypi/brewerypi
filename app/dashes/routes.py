from flask import render_template
from flask_login import login_required
from . import dashes

@dashes.route("/dashes/activeEventFramesSummary", methods = ["GET", "POST"])
@login_required
def activeEventFramesSummary():
	return render_template("activeEventFramesSummaryDash/activeEventFramesSummaryDash.html")

@dashes.route("/dashes/elementSummary", methods = ["GET", "POST"])
@login_required
def elementSummary():
	return render_template("elementSummaryDash/elementSummaryDash.html")

@dashes.route("/dashes/elementValuesGraph", methods = ["GET", "POST"])
@login_required
def elementValuesGraph():
	return render_template("elementValuesGraphDash/elementValuesGraphDash.html")

@dashes.route("/dashes/eventFrameGroupSummary", methods = ["GET", "POST"])
@login_required
def eventFrameGroupSummary():
	return render_template("eventFrameGroupSummaryDash/eventFrameGroupSummaryDash.html")

@dashes.route("/dashes/eventFrameGraph", methods = ["GET", "POST"])
@login_required
def eventFrameGraph():
	return render_template("eventFrameGraphDash/eventFrameGraphDash.html")

@dashes.route("/dashes/eventFramesOverlay", methods = ["GET", "POST"])
@login_required
def eventFramesOverlay():
	return render_template("eventFramesOverlayDash/eventFramesOverlayDash.html")

@dashes.route("/dashes/tagValuesGraph", methods = ["GET", "POST"])
@login_required
def tagValuesGraph():
	return render_template("tagValuesGraphDash/tagValuesGraphDash.html")
