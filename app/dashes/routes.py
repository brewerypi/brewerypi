from flask import render_template
from flask_login import login_required
from app.models import ElementTemplate, Site, Tag
from . import dashes

@dashes.route("/dashes/activeEventFramesSummary", methods = ["GET", "POST"])
@login_required
def activeEventFramesSummary():
	return render_template("dashes/activeEventFramesSummary/activeEventFramesSummary.html")

@dashes.route("/dashes/elementSummary", methods = ["GET", "POST"])
@dashes.route("/dashes/elementSummary/<string:idType>/<int:id>", methods = ["GET", "POST"])
@login_required
def elementSummary(idType = None, id = None):
	site = None,
	elementTemplate = None
	if idType == "site":
		site = Site.query.filter_by(SiteId = id).one_or_none()
	elif idType == "elementTemplate":
		elementTemplate = ElementTemplate.query.filter_by(ElementTemplateId = id).one_or_none()

	return render_template("dashes/elementSummary/elementSummary.html", elementTemplate = elementTemplate, site = site)

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
@dashes.route("/dashes/tagValuesGraph/<int:tagId>", methods = ["GET", "POST"])
@login_required
def tagValuesGraph(tagId = None):
	tag = Tag.query.filter_by(TagId = tagId).one_or_none()
	return render_template("dashes/tagValuesGraph/tagValuesGraph.html", tag = tag)
