from flask import render_template
from flask_login import login_required
from . import dash

@dash.route("/dash/activeEventFramesSummary", methods = ["GET", "POST"])
@login_required
def activeEventFramesSummary():
	return render_template("activeEventFramesSummaryDash/activeEventFramesSummaryDash.html")

@dash.route("/dash/elementSummary", methods = ["GET", "POST"])
@login_required
def elementSummary():
	return render_template("elementSummaryDash/elementSummaryDash.html")

@dash.route("/dash/elementValuesGraph", methods = ["GET", "POST"])
@login_required
def elementValuesGraph():
	return render_template("elementValuesGraphDash/elementValuesGraphDash.html")

@dash.route("/dash/eventFrameGroupSummary", methods = ["GET", "POST"])
@login_required
def eventFrameGroupSummary():
	return render_template("eventFrameGroupSummaryDash/eventFrameGroupSummaryDash.html")

@dash.route("/dash/eventFramesGraph", methods = ["GET", "POST"])
@login_required
def eventFramesGraph():
	return render_template("eventFramesGraphDash/eventFramesGraphDash.html")

@dash.route("/dash/eventFramesOverlay", methods = ["GET", "POST"])
@login_required
def eventFramesOverlay():
	return render_template("eventFramesOverlayDash/eventFramesOverlayDash.html")

@dash.route("/dash/tagValuesGraph", methods = ["GET", "POST"])
@login_required
def tagValuesGraph():
	return render_template("tagValuesGraphDash/tagValuesGraphDash.html")
