from datetime import datetime
from flask import flash, redirect, render_template, request
from flask_login import login_required
from . import eventFramesOverlay
from . forms import EventFramesOverlayForm
from .. eventFrames.sql import currentEventFrameAttributeValues
from .. decorators import permissionRequired
from .. models import ElementTemplate, Enterprise, EventFrame, EventFrameAttributeTemplate, EventFrameTemplate, Permission, Site

@eventFramesOverlay.route("/eventFramesOverlay/builder/<int:eventFrameTemplateId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def builder(eventFrameTemplateId):
	eventFrameTemplate = EventFrameTemplate.query.get_or_404(eventFrameTemplateId)
	eventFrameAttributeTemplates = EventFrameAttributeTemplate.query.filter_by(EventFrameTemplateId = eventFrameTemplateId)
	form = EventFramesOverlayForm()
	if form.validate_on_submit():
		startTimestamp = datetime.strptime(request.form.get("startUtcTimestamp"), "%Y-%m-%d %H:%M:%S")
		endUtcTimestamp = request.form.get("endUtcTimestamp")
		if endUtcTimestamp == "":
			endTimestamp = datetime.utcnow().replace(microsecond = 0)
		else:
			endTimestamp = datetime.strptime(endUtcTimestamp, "%Y-%m-%d %H:%M:%S")

		eventFrames = EventFrame.query.filter(EventFrame.EventFrameTemplateId == eventFrameTemplateId, EventFrame.StartTimestamp >= startTimestamp,
			EventFrame.StartTimestamp <= endTimestamp)
		eventFrames = currentEventFrameAttributeValues(eventFrames, eventFrameTemplateId)
		return render_template("eventFramesOverlay/builder.html", endTimestamp = endTimestamp, eventFrames = eventFrames,
			eventFrameAttributeTemplates = eventFrameAttributeTemplates, eventFrameTemplate = eventFrameTemplate, startTimestamp = startTimestamp)

	return render_template("eventFramesOverlay/builder.html", eventFrameAttributeTemplates = eventFrameAttributeTemplates,
		eventFrameTemplate = eventFrameTemplate, form = form)

@eventFramesOverlay.route("/eventFramesOverlay/select", methods = ["GET", "POST"]) # Default.
@eventFramesOverlay.route("/eventFramesOverlay/select/<string:selectedClass>", methods = ["GET", "POST"]) # Root.
@eventFramesOverlay.route("/eventFramesOverlay/select/<string:selectedClass>/<int:selectedId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def selectEventFrameTemplate(selectedClass = None, selectedId = None):
	eventFrameAttributeTemplates = None
	if selectedClass == None:
		parent = Site.query.join(Enterprise).order_by(Enterprise.Name, Site.Name).first()
		if parent is None:
			flash("You must create a Site first.", "alert alert-danger")
			return redirect(request.referrer)
		else:
			children = ElementTemplate.query.filter_by(SiteId = parent.id())
			childrenClass = "ElementTemplate"
	elif selectedClass == "Root":
		parent = None
		children = Enterprise.query.order_by(Enterprise.Name)
		childrenClass = "Enterprise"
	elif selectedClass == "Enterprise":
		parent = Enterprise.query.get_or_404(selectedId)
		children = Site.query.filter_by(EnterpriseId = selectedId)
		childrenClass = "Site"
	elif selectedClass == "Site":
		parent = Site.query.get_or_404(selectedId)
		children = ElementTemplate.query.filter_by(SiteId = selectedId)
		childrenClass = "ElementTemplate"
	elif selectedClass == "ElementTemplate":
		parent = ElementTemplate.query.get_or_404(selectedId)
		children = EventFrameTemplate.query.filter_by(ElementTemplateId = selectedId)
		childrenClass = "EventFrameTemplate"

	return render_template("eventFramesOverlay/select.html", children = children, childrenClass = childrenClass, parent = parent)
