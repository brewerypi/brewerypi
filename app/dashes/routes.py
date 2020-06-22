from flask import render_template
from flask_login import login_required
from . import dashes

@dashes.route("/dashes/activeEventFramesSummary", methods = ["GET", "POST"])
@login_required
def activeEventFramesSummary():
	return render_template("dashes/activeEventFramesSummary/activeEventFramesSummary.html")

@dashes.route("/dashes/elementSummary", methods = ["GET", "POST"])
@login_required
def elementSummary():
	return render_template("dashes/elementSummary/elementSummary.html")

@dashes.route("/dashes/elementValuesGraph", methods = ["GET", "POST"])
@login_required
def elementValuesGraph():
	return render_template("dashes/elementValuesGraph/elementValuesGraph.html")

@dashes.route("/dashes/eventFrameGroupSummary", methods = ["GET", "POST"])
@login_required
def eventFrameGroupSummary():
	return render_template("dashes/eventFrameGroupSummary/eventFrameGroupSummary.html")

@dashes.route("/dashes/eventFrameGraph", methods = ["GET", "POST"])
@login_required
def eventFrameGraph():
	return render_template("dashes/eventFrameGraph/eventFrameGraph.html")

@dashes.route("/dashes/eventFramesOverlay", methods = ["GET", "POST"])
@login_required
def eventFramesOverlay():
	return render_template("dashes/eventFramesOverlay/eventFramesOverlay.html")

@dashes.route("/dashes/tagValuesGraph", methods = ["GET", "POST"])
@login_required
def tagValuesGraph():
	return render_template("dashes/tagValuesGraph/tagValuesGraph.html")
