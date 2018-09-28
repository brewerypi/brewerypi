from datetime import datetime
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from . import eventFrames
from . forms import EventFrameForm, EventFrameOverlayForm
from .. import db
from .. decorators import permissionRequired
from .. models import Element, ElementTemplate, Enterprise, EventFrame, EventFrameAttribute, EventFrameAttributeTemplate, EventFrameTemplate, Lookup, \
	LookupValue, Permission, Site, Tag, TagValue

modelName = "Event Frame"

@eventFrames.route("/eventFrames/add/<int:eventFrameTemplateId>", methods = ["GET", "POST"])
@eventFrames.route("/eventFrames/add/child/<int:parentEventFrameId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def addEventFrame(eventFrameTemplateId = None, parentEventFrameId = None):
	operation = "Add"
	form = EventFrameForm()
	if parentEventFrameId:
		del form.element
		parentEventFrame = EventFrame.query.get_or_404(parentEventFrameId)
		form.eventFrameTemplate.query = EventFrameTemplate.query. \
			filter(EventFrameTemplate.ParentEventFrameTemplateId == parentEventFrame.EventFrameTemplateId).order_by(EventFrameTemplate.Name)
	else:
		del form.eventFrameTemplate
		eventFrameTemplate = EventFrameTemplate.query.get_or_404(eventFrameTemplateId)
		form.element.query = Element.query.join(ElementTemplate).filter(ElementTemplate.ElementTemplateId == eventFrameTemplate.ElementTemplateId). \
			order_by(Element.Name)

	# Add a new event frame.
	if form.validate_on_submit():
		if parentEventFrameId:
			eventFrame = EventFrame(EndTimestamp = form.endTimestamp.data, EventFrameTemplate = form.eventFrameTemplate.data,
				Name = form.name.data, ParentEventFrameId = parentEventFrameId, StartTimestamp = form.startTimestamp.data)
		else:
			eventFrame = EventFrame(Element = form.element.data, EndTimestamp = form.endTimestamp.data, EventFrameTemplateId = eventFrameTemplateId,
				Name = form.name.data, StartTimestamp = form.startTimestamp.data)

		db.session.add(eventFrame)
		db.session.commit()
		flash("You have successfully added a new Event Frame.", "alert alert-success")
		return redirect(form.requestReferrer.data)

	form.requestReferrer.data = request.referrer
	if parentEventFrameId:
		form.parentEventFrameId.data = parentEventFrameId
		breadcrumbs = [{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\">"},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Enterprise",
				selectedId = parentEventFrame.origin().Element.ElementTemplate.Site.Enterprise.EnterpriseId),
				"text" : parentEventFrame.origin().Element.ElementTemplate.Site.Enterprise.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Site",
				selectedId = parentEventFrame.origin().Element.ElementTemplate.Site.SiteId),
				"text" : parentEventFrame.origin().Element.ElementTemplate.Site.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "ElementTemplate",
				selectedId = parentEventFrame.origin().Element.ElementTemplate.ElementTemplateId),
				"text" : parentEventFrame.origin().Element.ElementTemplate.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "EventFrameTemplate",
				selectedId = parentEventFrame.origin().EventFrameTemplate.EventFrameTemplateId),
				"text" : parentEventFrame.origin().EventFrameTemplate.Name}]
		for eventFrameAncestor in parentEventFrame.ancestors([]):
			if eventFrameAncestor.ParentEventFrameId:
				text = eventFrameAncestor.EventFrameTemplate.Name + "&nbsp;&nbsp;/&nbsp;&nbsp;" + eventFrameAncestor.friendlyName(True)
			else:
				text = eventFrameAncestor.friendlyName(True)
			breadcrumbs.append({"url" : url_for("eventFrames.dashboard", eventFrameId = eventFrameAncestor.EventFrameId), "text" : text})

		if parentEventFrame.ParentEventFrameId:
			text = parentEventFrame.EventFrameTemplate.Name + "&nbsp;&nbsp;/&nbsp;&nbsp;" + parentEventFrame.friendlyName(True)
		else:
			text = parentEventFrame.friendlyName(True)
		breadcrumbs.append({"url" : url_for("eventFrames.dashboard", eventFrameId = parentEventFrame.EventFrameId), "text" : text})
	else:
		form.eventFrameTemplateId.data = eventFrameTemplateId
		breadcrumbs = [{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\">"},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Enterprise",
				selectedId = eventFrameTemplate.ElementTemplate.Site.Enterprise.EnterpriseId),
				"text" : eventFrameTemplate.ElementTemplate.Site.Enterprise.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Site", selectedId = eventFrameTemplate.ElementTemplate.Site.SiteId),
				"text" : eventFrameTemplate.ElementTemplate.Site.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "ElementTemplate",
				selectedId = eventFrameTemplate.ElementTemplate.ElementTemplateId),
				"text" : eventFrameTemplate.ElementTemplate.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "EventFrameTemplate", selectedId = eventFrameTemplate.EventFrameTemplateId),
				"text" : eventFrameTemplate.Name}]	

	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@eventFrames.route("/eventFrames/dashboard/<int:eventFrameId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def dashboard(eventFrameId):
	eventFrame = EventFrame.query.get_or_404(eventFrameId)
	if eventFrame.ElementId:
		elementId = eventFrame.ElementId
	else:
		elementId = eventFrame.origin().ElementId

	eventFrameAttributes = EventFrameAttribute.query.join(EventFrameAttributeTemplate, EventFrameTemplate). \
		filter(EventFrameAttribute.ElementId == elementId, EventFrameTemplate.EventFrameTemplateId == eventFrame.EventFrameTemplate.EventFrameTemplateId)
	eventFrameAttributeIds = []
	for eventFrameAttribute in eventFrameAttributes:
		eventFrameAttributeIds.append(eventFrameAttribute.EventFrameAttributeId)

	if eventFrame.EndTimestamp:
		tagValues = TagValue.query.join(Tag, EventFrameAttribute).filter(EventFrameAttribute.EventFrameAttributeId.in_(eventFrameAttributeIds),
			TagValue.Timestamp >= eventFrame.StartTimestamp, TagValue.Timestamp <= eventFrame.EndTimestamp)
	else:
		tagValues = TagValue.query.join(Tag, EventFrameAttribute).filter(EventFrameAttribute.EventFrameAttributeId.in_(eventFrameAttributeIds),
			TagValue.Timestamp >= eventFrame.StartTimestamp)
	return render_template("eventFrames/dashboard.html", eventFrame = eventFrame, eventFrameAttributes = eventFrameAttributes, tagValues = tagValues)

@eventFrames.route("/eventFrames/delete/<int:eventFrameId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def deleteEventFrame(eventFrameId):
	eventFrame = EventFrame.query.get_or_404(eventFrameId)
	if eventFrame.hasDescendants():
		flash("This event frame contains one or more child event frames and cannot be deleted.", "alert alert-danger")
	else:
		db.session.delete(eventFrame)
		db.session.commit()
		flash("You have successfully deleted the event frame.", "alert alert-success")
	return redirect(request.referrer)

@eventFrames.route("/eventFrames/edit/<int:eventFrameId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def editEventFrame(eventFrameId):
	operation = "Edit"
	eventFrame = EventFrame.query.get_or_404(eventFrameId)
	form = EventFrameForm(obj = eventFrame)
	if eventFrame.ParentEventFrameId:
		del form.element
		form.eventFrameTemplate.query = EventFrameTemplate.query. \
			filter(EventFrameTemplate.ParentEventFrameTemplateId == eventFrame.ParentEventFrame.EventFrameTemplateId).order_by(EventFrameTemplate.Name)
	else:
		del form.eventFrameTemplate
		form.element.query = Element.query.join(ElementTemplate).filter(ElementTemplate.ElementTemplateId == eventFrame.EventFrameTemplate.ElementTemplateId). \
			order_by(Element.Name)

	# Edit an existing event frame.
	if form.validate_on_submit():
		if eventFrame.ParentEventFrameId:
			eventFrame.EventFrameTemplate = form.eventFrameTemplate.data
			eventFrame.ParentEventFrameId = form.parentEventFrameId.data
		else:
			eventFrame.Element = form.element.data
			eventFrame.EventFrameTemplateId = form.eventFrameTemplateId.data

		eventFrame.EndTimestamp = form.endTimestamp.data
		eventFrame.Name = form.name.data
		eventFrame.StartTimestamp = form.startTimestamp.data
		db.session.commit()
		flash("You have successfully edited the Event Frame.", "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to edit an existing event frame.
	if eventFrame.ParentEventFrameId:
		form.eventFrameTemplate.data = eventFrame.EventFrameTemplate
		form.parentEventFrameId.data = eventFrame.ParentEventFrameId
		breadcrumbs = [{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\">"},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Enterprise",
				selectedId = eventFrame.origin().Element.ElementTemplate.Site.Enterprise.EnterpriseId),
				"text" : eventFrame.origin().Element.ElementTemplate.Site.Enterprise.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Site",
				selectedId = eventFrame.origin().Element.ElementTemplate.Site.SiteId),
				"text" : eventFrame.origin().Element.ElementTemplate.Site.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "ElementTemplate",
				selectedId = eventFrame.origin().Element.ElementTemplate.ElementTemplateId),
				"text" : eventFrame.origin().Element.ElementTemplate.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "EventFrameTemplate",
				selectedId = eventFrame.origin().EventFrameTemplate.EventFrameTemplateId),
				"text" : eventFrame.origin().EventFrameTemplate.Name}]
		for eventFrameAncestor in eventFrame.ancestors([]):
			if eventFrameAncestor.ParentEventFrameId:
				text = eventFrameAncestor.EventFrameTemplate.Name + "&nbsp;&nbsp;/&nbsp;&nbsp;" + eventFrameAncestor.friendlyName(True)
			else:
				text = eventFrameAncestor.friendlyName(True)
			breadcrumbs.append({"url" : url_for("eventFrames.dashboard", eventFrameId = eventFrameAncestor.EventFrameId), "text" : text})

		if eventFrame.ParentEventFrameId:
			text = eventFrame.EventFrameTemplate.Name + "&nbsp;&nbsp;/&nbsp;&nbsp;" + eventFrame.friendlyName(True)
		else:
			text = eventFrame.friendlyName(True)
		breadcrumbs.append({"url" : None, "text" : text})
	else:
		form.element.data = eventFrame.Element
		form.eventFrameTemplateId.data = eventFrame.EventFrameTemplateId
		breadcrumbs = [{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\">"},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Enterprise",
				selectedId = eventFrame.EventFrameTemplate.ElementTemplate.Site.Enterprise.EnterpriseId),
				"text" : eventFrame.EventFrameTemplate.ElementTemplate.Site.Enterprise.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Site", selectedId = eventFrame.EventFrameTemplate.ElementTemplate.Site.SiteId),
				"text" : eventFrame.EventFrameTemplate.ElementTemplate.Site.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "ElementTemplate",
				selectedId = eventFrame.EventFrameTemplate.ElementTemplate.ElementTemplateId), "text" : eventFrame.EventFrameTemplate.ElementTemplate.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "EventFrameTemplate",
				selectedId = eventFrame.EventFrameTemplate.EventFrameTemplateId), "text" : eventFrame.EventFrameTemplate.Name},
			{"url" : None, "text" : eventFrame.friendlyName(True)}]	

	form.endTimestamp.data = eventFrame.EndTimestamp
	form.name.data = eventFrame.Name
	form.startTimestamp.data = eventFrame.StartTimestamp
	form.requestReferrer.data = request.referrer
	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@eventFrames.route("/eventFrames/endEventFrame/<int:eventFrameId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def endEventFrame(eventFrameId):
	eventFrame = EventFrame.query.get_or_404(eventFrameId)
	eventFrame.EndTimestamp = datetime.now()
	db.session.commit()
	flash("You have successfully ended \"{}\" for event frame \"{}\".".format(eventFrame.EventFrameTemplate.Name, eventFrame.friendlyName(True)),
		"alert alert-success")
	return redirect(request.referrer)

@eventFrames.route("/eventFrames/select", methods = ["GET", "POST"]) # Default.
@eventFrames.route("/eventFrames/select/<string:selectedClass>", methods = ["GET", "POST"]) # Root.
@eventFrames.route("/eventFrames/select/<string:selectedClass>/<int:selectedId>", methods = ["GET", "POST"])
@eventFrames.route("/eventFrames/select/<string:selectedClass>/<int:selectedId>/<string:selectedOperation>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def selectEventFrame(selectedClass = None, selectedId = None, selectedOperation = None):
	eventFrameAttributeTemplates = None
	if selectedClass == None:
		parent = Site.query.join(Enterprise, ElementTemplate, EventFrameTemplate, EventFrame).order_by(Enterprise.Name).first()
		if parent:
			children = ElementTemplate.query.filter_by(SiteId = parent.id())
		else:
			parent = Site.query.join(Enterprise, ElementTemplate).order_by(Enterprise.Name).first()
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
	elif selectedClass == "EventFrameTemplate" and selectedOperation == "configure":
		parent = EventFrameTemplate.query.get_or_404(selectedId)
		children = EventFrameTemplate.query.filter_by(ParentEventFrameTemplateId = selectedId).order_by(EventFrameTemplate.Order)
		childrenClass = "DescendantEventFrameTemplate"
		eventFrameAttributeTemplates = EventFrameAttributeTemplate.query.filter_by(EventFrameTemplateId = selectedId). \
			order_by(EventFrameAttributeTemplate.Name)
	elif selectedClass == "EventFrameTemplate":
		parent = EventFrameTemplate.query.get_or_404(selectedId)
		children = EventFrame.query.filter_by(EventFrameTemplateId = selectedId)
		childrenClass = "EventFrame"

	return render_template("eventFrames/select.html", children = children, childrenClass = childrenClass,
		eventFrameAttributeTemplates = eventFrameAttributeTemplates, parent = parent)

@eventFrames.route("/eventFrames/overlay/<int:eventFrameTemplateId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def overlay(eventFrameTemplateId):
	form = EventFrameOverlayForm()

	if form.validate_on_submit():
		if form.endTimestamp.data:
			eventFrames = EventFrame.query.filter(EventFrame.EventFrameTemplateId == eventFrameTemplateId,
				EventFrame.StartTimestamp >= form.startTimestamp.data, EventFrame.EndTimestamp <= form.endTimestamp.data)
		else:
			eventFrames = EventFrame.query.join(EventFrameTemplate, EventFrameAttributeTemplate, EventFrameAttribute, Element, Tag). \
				outerjoin(Lookup, LookupValue). \
				filter(EventFrame.EventFrameTemplateId == eventFrameTemplateId, EventFrame.StartTimestamp >= form.startTimestamp.data)
		return render_template("eventFrames/overlay.html", eventFrames = eventFrames)

	return render_template("eventFrames/overlay.html", form = form)

@eventFrames.route("/eventFrames/startEventFrame/<int:elementId>/<int:eventFrameTemplateId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def startEventFrame(elementId, eventFrameTemplateId):
	eventFrame = EventFrame(ElementId = elementId, EndTimestamp = None, EventFrameTemplateId = eventFrameTemplateId, ParentEventFrameId = None,
		StartTimestamp = datetime.now())
	db.session.add(eventFrame)
	db.session.commit()
	flash("You have successfully added a new \"" + eventFrame.EventFrameTemplate.Name + "\" for element \"" + eventFrame.origin().Element.Name + "\".",
		"alert alert-success")
	return redirect(request.referrer)
