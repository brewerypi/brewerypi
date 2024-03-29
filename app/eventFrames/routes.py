from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required
from operator import itemgetter
from . import eventFrames
from . forms import EventFrameForm
from . sql import currentEventFrameAttributeValues
from .. import db
from .. decorators import permissionRequired
from .. models import Element, ElementTemplate, Enterprise, EventFrame, EventFrameAttribute, EventFrameAttributeTemplate, \
	EventFrameAttributeTemplateEventFrameTemplateView, EventFrameEventFrameGroup, EventFrameGroup, EventFrameTemplate, EventFrameTemplateView, \
	Lookup, LookupValue, Permission, Site, Tag, TagValue

modelName = "Event Frame"

@eventFrames.route("/eventFrames/add/<int:eventFrameTemplateId>", methods = ["GET", "POST"])
@eventFrames.route("/eventFrames/add/child/<int:parentEventFrameId>", methods = ["GET", "POST"])
@eventFrames.route("/eventFrames/add/child/<int:parentEventFrameId>/<int:eventFrameGroupId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def addEventFrame(eventFrameTemplateId = None, parentEventFrameId = None, eventFrameGroupId = None):
	operation = "Add"
	form = EventFrameForm()
	if parentEventFrameId:
		parentEventFrame = EventFrame.query.get_or_404(parentEventFrameId)
		form.element.query = Element.query.join(EventFrame).filter(EventFrame.ElementId == parentEventFrame.origin().ElementId)
		form.eventFrameTemplate.query = EventFrameTemplate.query. \
			filter(EventFrameTemplate.ParentEventFrameTemplateId == parentEventFrame.EventFrameTemplateId).order_by(EventFrameTemplate.Order)
	else:
		eventFrameTemplate = EventFrameTemplate.query.get_or_404(eventFrameTemplateId)
		form.element.query = Element.query.join(ElementTemplate).filter(ElementTemplate.ElementTemplateId == eventFrameTemplate.ElementTemplateId). \
			order_by(Element.Name)
		form.eventFrameTemplate.query = EventFrameTemplate.query.filter_by(EventFrameTemplateId = eventFrameTemplateId)

	sourceEventFrameTemplateChoices = [(0, "")]
	for sourceEventFrameTemplate in EventFrameTemplate.query.order_by(EventFrameTemplate.Name).all():
		sourceEventFrameTemplateChoices.append((sourceEventFrameTemplate.EventFrameTemplateId, sourceEventFrameTemplate.fullyQualifiedName()))

	form.sourceEventFrameTemplate.choices = sorted(sourceEventFrameTemplateChoices, key = itemgetter(1))
	sourceEventFrameChoices = [(-1, "")]
	for sourceEventFrame in EventFrame.query.order_by(EventFrame.Name).all():
		sourceEventFrameChoices.append((sourceEventFrame.EventFrameId, sourceEventFrame.fullyQualifiedName()))

	form.sourceEventFrame.choices = sorted(sourceEventFrameChoices, key = itemgetter(1))

	# Add a new event frame.
	if form.validate_on_submit():
		if form.endUtcTimestamp.data == "":
			endUtcTimestamp = None
		else:
			endUtcTimestamp = form.endUtcTimestamp.data

		sourceEventFrameId = None if form.sourceEventFrame.data == -1 else form.sourceEventFrame.data
		if parentEventFrameId:
			eventFrame = EventFrame(EndTimestamp = endUtcTimestamp, EventFrameTemplate = form.eventFrameTemplate.data, SourceEventFrameId = sourceEventFrameId,
				Name = form.name.data, ParentEventFrameId = parentEventFrameId, StartTimestamp = form.startUtcTimestamp.data, UserId = current_user.get_id())
		else:
			eventFrame = EventFrame(Element = form.element.data, EndTimestamp = endUtcTimestamp, EventFrameTemplateId = eventFrameTemplateId,
				SourceEventFrameId = sourceEventFrameId, Name = form.name.data, StartTimestamp = form.startUtcTimestamp.data, UserId = current_user.get_id())

		db.session.add(eventFrame)
		db.session.commit()
		eventFrame.addDefaultAttributeTemplateValues(form.startUtcTimestamp.data)
		db.session.commit()

		flash("You have successfully added a new Event Frame.", "alert alert-success")
		return redirect(form.requestReferrer.data)

	if form.requestReferrer.data is None:
		form.requestReferrer.data = request.referrer
	
	if eventFrameGroupId is None:
		eventFrameGroup = None
	else:
		eventFrameGroup = EventFrameGroup.query.get_or_404(eventFrameGroupId)

	if parentEventFrameId is None:
		form.eventFrameTemplateId.data = eventFrameTemplateId
		breadcrumbs = [{"url": url_for("eventFrames.selectEventFrame", selectedClass = "Root"),
			"text": "<span class = \"glyphicon glyphicon-home\"></span>"},
			{"url": url_for("eventFrames.selectEventFrame", selectedClass = "Enterprise",
				selectedId = eventFrameTemplate.ElementTemplate.Site.Enterprise.EnterpriseId),
				"text": eventFrameTemplate.ElementTemplate.Site.Enterprise.Name},
			{"url": url_for("eventFrames.selectEventFrame", selectedClass = "Site", selectedId = eventFrameTemplate.ElementTemplate.Site.SiteId),
				"text": eventFrameTemplate.ElementTemplate.Site.Name},
			{"url": url_for("eventFrames.selectEventFrame", selectedClass = "ElementTemplate",
				selectedId = eventFrameTemplate.ElementTemplate.ElementTemplateId),
				"text": eventFrameTemplate.ElementTemplate.Name},
			{"url": url_for("eventFrames.selectEventFrame", selectedClass = "EventFrameTemplate", selectedId = eventFrameTemplate.EventFrameTemplateId),
				"text": eventFrameTemplate.Name}]	
	else:
		form.parentEventFrameId.data = parentEventFrameId
		if eventFrameGroup is None:
			breadcrumbs = [{"url": url_for("eventFrames.selectEventFrame", selectedClass = "Root"),
				"text": "<span class = \"glyphicon glyphicon-home\"></span>"},
				{"url": url_for("eventFrames.selectEventFrame", selectedClass = "Enterprise",
					selectedId = parentEventFrame.origin().Element.ElementTemplate.Site.Enterprise.EnterpriseId),
					"text": parentEventFrame.origin().Element.ElementTemplate.Site.Enterprise.Name},
				{"url": url_for("eventFrames.selectEventFrame", selectedClass = "Site",
					selectedId = parentEventFrame.origin().Element.ElementTemplate.Site.SiteId),
					"text": parentEventFrame.origin().Element.ElementTemplate.Site.Name},
				{"url": url_for("eventFrames.selectEventFrame", selectedClass = "ElementTemplate",
					selectedId = parentEventFrame.origin().Element.ElementTemplate.ElementTemplateId),
					"text": parentEventFrame.origin().Element.ElementTemplate.Name},
				{"url": url_for("eventFrames.selectEventFrame", selectedClass = "EventFrameTemplate",
					selectedId = parentEventFrame.origin().EventFrameTemplate.EventFrameTemplateId),
					"text": parentEventFrame.origin().EventFrameTemplate.Name}]
			for eventFrameAncestor in parentEventFrame.ancestors([]):
				if eventFrameAncestor.ParentEventFrameId is None:
					text = eventFrameAncestor.Name
				else:
					text = "{} / {}".format(eventFrameAncestor.EventFrameTemplate.Name, eventFrameAncestor.Name)

				breadcrumbs.append({"url": url_for("eventFrames.dashboard", eventFrameId = eventFrameAncestor.EventFrameId), "text": text})

			if parentEventFrame.ParentEventFrameId is None:
				text = parentEventFrame.Name
			else:
				text = "{} / {}".format(parentEventFrame.EventFrameTemplate.Name, parentEventFrame.Name)

			breadcrumbs.append({"url": url_for("eventFrames.dashboard", eventFrameId = parentEventFrame.EventFrameId), "text": text})
		else:
			breadcrumbs = [{"url": url_for("eventFrameGroups.listEventFrameGroups"), "text": "<span class = \"glyphicon glyphicon-home\"></span>"},
				{"url": url_for("eventFrameGroups.dashboard", eventFrameGroupId = eventFrameGroup.EventFrameGroupId), "text": eventFrameGroup.Name}]
			for eventFrameAncestor in parentEventFrame.ancestors([]):
				if eventFrameAncestor.ParentEventFrameId is not None:
					breadcrumbs.append({"url": url_for("eventFrames.dashboard", eventFrameId = eventFrameAncestor.EventFrameId,
						eventFrameGroupId = eventFrameGroup.EventFrameGroupId),
						"text": "{} / {}".format(eventFrameAncestor.EventFrameTemplate.Name, eventFrameAncestor.Name)})
				else:
					breadcrumbs.append({"url": url_for("eventFrames.dashboard", eventFrameId = eventFrameAncestor.EventFrameId,
						eventFrameGroupId = eventFrameGroup.EventFrameGroupId),
						"text": eventFrameAncestor.Name})

			if parentEventFrame.ParentEventFrameId is None:
				breadcrumbs.append({"url": url_for("eventFrames.dashboard", eventFrameId = parentEventFrame.EventFrameId,
					eventFrameGroupId = eventFrameGroup.EventFrameGroupId),
					"text": parentEventFrame.Name})
			else:
				breadcrumbs.append({"url": url_for("eventFrames.dashboard", eventFrameId = parentEventFrame.EventFrameId,
					eventFrameGroupId = eventFrameGroup.EventFrameGroupId),
					"text": "{} / {}".format(parentEventFrame.EventFrameTemplate.Name, parentEventFrame.Name)})

	return render_template("eventFrames/addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@eventFrames.route("/eventFrames/dashboard/<int:eventFrameId>", methods = ["GET", "POST"])
@eventFrames.route("/eventFrames/dashboard/<int:eventFrameId>/<int:eventFrameTemplateView>/<int:eventFrameTemplateViewId>", methods = ["GET", "POST"])
@eventFrames.route("/eventFrames/dashboard/<int:eventFrameId>/<int:eventFrameGroupId>", methods = ["GET", "POST"])
@eventFrames.route("/eventFrames/dashboard/<int:eventFrameId>/<int:eventFrameGroupId>/<int:eventFrameTemplateView>/<int:eventFrameTemplateViewId>",
	methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def dashboard(eventFrameId, eventFrameGroupId = None, eventFrameTemplateView = None, eventFrameTemplateViewId = None):
	eventFrame = EventFrame.query.get_or_404(eventFrameId)
	if eventFrame.ElementId:
		elementId = eventFrame.ElementId
	else:
		elementId = eventFrame.origin().ElementId
	
	if eventFrameGroupId is None:
		eventFrameEventFrameGroup = None
	else:
		eventFrameEventFrameGroup = EventFrameEventFrameGroup.query.filter_by(EventFrameGroupId = eventFrameGroupId,
			EventFrameId = eventFrame.origin().EventFrameId).one_or_none()

	if eventFrameTemplateViewId is None:
		defaultEventFrameTemplateView = EventFrameTemplateView.query.filter_by(EventFrameTemplateId = eventFrame.EventFrameTemplateId,
			Default = True).one_or_none()
		if defaultEventFrameTemplateView is None:
			eventFrameTemplateView = None
			eventFrameAttributes = EventFrameAttribute.query.join(EventFrameAttributeTemplate).join(EventFrameTemplate). \
				filter(EventFrameAttribute.ElementId == elementId,
				EventFrameTemplate.EventFrameTemplateId == eventFrame.EventFrameTemplate.EventFrameTemplateId). \
				order_by(EventFrameAttributeTemplate.Name)
		else:
			eventFrameTemplateView = defaultEventFrameTemplateView
			eventFrameAttributes = EventFrameAttribute.query.join(EventFrameAttributeTemplate).join(EventFrameTemplate). \
				join(EventFrameAttributeTemplateEventFrameTemplateView).filter(EventFrameAttribute.ElementId == elementId,
				EventFrameTemplate.EventFrameTemplateId == eventFrame.EventFrameTemplate.EventFrameTemplateId,
				EventFrameAttributeTemplateEventFrameTemplateView.EventFrameTemplateViewId == defaultEventFrameTemplateView.EventFrameTemplateViewId). \
				order_by(EventFrameAttributeTemplateEventFrameTemplateView.Order)
	elif  eventFrameTemplateViewId == 0:
		eventFrameTemplateView = EventFrameTemplateView(EventFrameTemplateViewId = 0, Name = "All")
		eventFrameAttributes = EventFrameAttribute.query.join(EventFrameAttributeTemplate).join(EventFrameTemplate). \
			filter(EventFrameAttribute.ElementId == elementId, EventFrameTemplate.EventFrameTemplateId == eventFrame.EventFrameTemplate.EventFrameTemplateId). \
			order_by(EventFrameAttributeTemplate.Name)
	else:
		eventFrameTemplateView = EventFrameTemplateView.query.get_or_404(eventFrameTemplateViewId)
		eventFrameAttributes = EventFrameAttribute.query.join(EventFrameAttributeTemplate).join(EventFrameTemplate). \
			join(EventFrameAttributeTemplateEventFrameTemplateView).filter(EventFrameAttribute.ElementId == elementId,
			EventFrameTemplate.EventFrameTemplateId == eventFrame.EventFrameTemplate.EventFrameTemplateId,
			EventFrameAttributeTemplateEventFrameTemplateView.EventFrameTemplateViewId == eventFrameTemplateViewId). \
			order_by(EventFrameAttributeTemplateEventFrameTemplateView.Order)

	eventFrameAttributeIds = []
	for eventFrameAttribute in eventFrameAttributes:
		eventFrameAttributeIds.append(eventFrameAttribute.EventFrameAttributeId)

	return render_template("eventFrames/dashboard.html", eventFrame = eventFrame, eventFrameEventFrameGroup = eventFrameEventFrameGroup,
		eventFrameAttributes = eventFrameAttributes, eventFrameTemplateView = eventFrameTemplateView)

@eventFrames.route("/eventFrames/delete/<int:eventFrameId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def deleteEventFrame(eventFrameId):
	eventFrame = EventFrame.query.get_or_404(eventFrameId)
	eventFrame.delete()
	db.session.commit()
	flash("You have successfully deleted the event frame.", "alert alert-success")
	return redirect(request.referrer)

@eventFrames.route("/eventFrames/edit/<int:eventFrameId>", methods = ["GET", "POST"])
@eventFrames.route("/eventFrames/edit/<int:eventFrameId>/<int:eventFrameGroupId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def editEventFrame(eventFrameId, eventFrameGroupId = None):
	operation = "Edit"
	eventFrame = EventFrame.query.get_or_404(eventFrameId)
	form = EventFrameForm(obj = eventFrame)
	del form.eventFrameTemplate
	if eventFrame.ParentEventFrameId is None:
		form.element.query = Element.query.join(ElementTemplate).filter(ElementTemplate.ElementTemplateId == eventFrame.EventFrameTemplate.ElementTemplateId). \
			order_by(Element.Name)
	else:
		del form.element

	sourceEventFrameTemplateChoices = [(0, "")]
	for sourceEventFrameTemplate in EventFrameTemplate.query.order_by(EventFrameTemplate.Name).all():
		sourceEventFrameTemplateChoices.append((sourceEventFrameTemplate.EventFrameTemplateId, sourceEventFrameTemplate.fullyQualifiedName()))

	form.sourceEventFrameTemplate.choices = sorted(sourceEventFrameTemplateChoices, key = itemgetter(1))
	sourceEventFrameChoices = [(-1, "")]
	for sourceEventFrame in EventFrame.query.order_by(EventFrame.Name).all():
		sourceEventFrameChoices.append((sourceEventFrame.EventFrameId, sourceEventFrame.fullyQualifiedName()))

	form.sourceEventFrame.choices = sorted(sourceEventFrameChoices, key = itemgetter(1))

	# Edit an existing event frame.
	if form.validate_on_submit():
		if eventFrame.ParentEventFrameId:
			eventFrame.ParentEventFrameId = form.parentEventFrameId.data
		else:
			eventFrame.Element = form.element.data

		if form.endUtcTimestamp.data == "":
			eventFrame.EndTimestamp = None
		else:
			eventFrame.EndTimestamp = form.endUtcTimestamp.data

		if form.sourceEventFrame.data == -1:
			eventFrame.SourceEventFrameId = None
		else:
			eventFrame.SourceEventFrameId = form.sourceEventFrame.data

		eventFrame.Name = form.name.data
		eventFrame.StartTimestamp = form.startUtcTimestamp.data
		eventFrame.UserId = current_user.get_id()
		db.session.commit()
		flash("You have successfully edited the Event Frame.", "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to edit an existing event frame.
	if eventFrameGroupId is None:
		eventFrameGroup = None
	else:
		eventFrameGroup = EventFrameGroup.query.get_or_404(eventFrameGroupId)

	if eventFrame.ParentEventFrameId is None:
		form.element.data = eventFrame.Element
		if eventFrameGroup is None:
			breadcrumbs = [{"url": url_for("eventFrames.selectEventFrame", selectedClass = "Root"),
				"text": "<span class = \"glyphicon glyphicon-home\"></span>"},
				{"url": url_for("eventFrames.selectEventFrame", selectedClass = "Enterprise",
					selectedId = eventFrame.EventFrameTemplate.ElementTemplate.Site.Enterprise.EnterpriseId),
					"text": eventFrame.EventFrameTemplate.ElementTemplate.Site.Enterprise.Name},
				{"url": url_for("eventFrames.selectEventFrame", selectedClass = "Site", selectedId = eventFrame.EventFrameTemplate.ElementTemplate.Site.SiteId),
					"text": eventFrame.EventFrameTemplate.ElementTemplate.Site.Name},
				{"url": url_for("eventFrames.selectEventFrame", selectedClass = "ElementTemplate",
					selectedId = eventFrame.EventFrameTemplate.ElementTemplate.ElementTemplateId), "text": eventFrame.EventFrameTemplate.ElementTemplate.Name},
				{"url": url_for("eventFrames.selectEventFrame", selectedClass = "EventFrameTemplate",
					selectedId = eventFrame.EventFrameTemplate.EventFrameTemplateId), "text": eventFrame.EventFrameTemplate.Name},
				{"url": None, "text": eventFrame.Name}]
		else:
			breadcrumbs = [{"url": url_for("eventFrameGroups.listEventFrameGroups"), "text": "<span class = \"glyphicon glyphicon-home\"></span>"},
				{"url": url_for("eventFrameGroups.dashboard", eventFrameGroupId = eventFrameGroup.EventFrameGroupId), "text": eventFrameGroup.Name},
				{"url": None, "text": eventFrame.Name}]
	else:
		form.parentEventFrameId.data = eventFrame.ParentEventFrameId
		if eventFrameGroup is None:
			breadcrumbs = [{"url": url_for("eventFrames.selectEventFrame", selectedClass = "Root"),
				"text": "<span class = \"glyphicon glyphicon-home\"></span>"},
				{"url": url_for("eventFrames.selectEventFrame", selectedClass = "Enterprise",
					selectedId = eventFrame.origin().Element.ElementTemplate.Site.Enterprise.EnterpriseId),
					"text": eventFrame.origin().Element.ElementTemplate.Site.Enterprise.Name},
				{"url": url_for("eventFrames.selectEventFrame", selectedClass = "Site",
					selectedId = eventFrame.origin().Element.ElementTemplate.Site.SiteId),
					"text": eventFrame.origin().Element.ElementTemplate.Site.Name},
				{"url": url_for("eventFrames.selectEventFrame", selectedClass = "ElementTemplate",
					selectedId = eventFrame.origin().Element.ElementTemplate.ElementTemplateId),
					"text": eventFrame.origin().Element.ElementTemplate.Name},
				{"url": url_for("eventFrames.selectEventFrame", selectedClass = "EventFrameTemplate",
					selectedId = eventFrame.origin().EventFrameTemplate.EventFrameTemplateId),
					"text": eventFrame.origin().EventFrameTemplate.Name}]
			for eventFrameAncestor in eventFrame.ancestors([]):
				if eventFrameAncestor.ParentEventFrameId is None:
					text = eventFrameAncestor.Name
				else:
					text = "{} / {}".format(eventFrameAncestor.EventFrameTemplate.Name, eventFrameAncestor.Name)

				breadcrumbs.append({"url": url_for("eventFrames.dashboard", eventFrameId = eventFrameAncestor.EventFrameId), "text": text})

			if eventFrame.ParentEventFrameId is None:
				text = eventFrame.Name
			else:
				text = "{} / {}".format(eventFrame.EventFrameTemplate.Name, eventFrame.Name)

			breadcrumbs.append({"url": None, "text": text})
		else:
			breadcrumbs = [{"url": url_for("eventFrameGroups.listEventFrameGroups"), "text": "<span class = \"glyphicon glyphicon-home\"></span>"},
				{"url": url_for("eventFrameGroups.dashboard", eventFrameGroupId = eventFrameGroup.EventFrameGroupId), "text": eventFrameGroup.Name}]
			for eventFrameAncestor in eventFrame.ancestors([]):
				if eventFrameAncestor.ParentEventFrameId:
					text = "{} / {}".format(eventFrameAncestor.EventFrameTemplate.Name, eventFrameAncestor.Name)
				else:
					text = eventFrameAncestor.Name
				breadcrumbs.append({"url": url_for("eventFrames.dashboard", eventFrameId = eventFrameAncestor.EventFrameId,
					eventFrameGroupId = eventFrameGroup.EventFrameGroupId), "text": text})

			if eventFrame.ParentEventFrameId:
				text = "{} / {}".format(eventFrame.EventFrameTemplate.Name, eventFrame.Name)
			else:
				text = eventFrame.Name

			breadcrumbs.append({"url": None, "text": text})

	form.sourceEventFrame.data = eventFrame.SourceEventFrameId
	form.eventFrameId.data = eventFrame.EventFrameId
	form.endTimestamp.data = eventFrame.EndTimestamp
	form.name.data = eventFrame.Name
	form.startTimestamp.data = eventFrame.StartTimestamp
	if form.requestReferrer.data is None:
		form.requestReferrer.data = request.referrer

	return render_template("eventFrames/addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@eventFrames.route("/eventFrames/endEventFrame/<int:eventFrameId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def endEventFrame(eventFrameId):
	eventFrame = EventFrame.query.get_or_404(eventFrameId)
	eventFrame.end()
	db.session.commit()
	flash('You have successfully ended "{}" for event frame "{}".'.format(eventFrame.EventFrameTemplate.Name, eventFrame.Name), "alert alert-success")
	return redirect(request.referrer)

@eventFrames.route("/eventFrames/getSourceEventFrames/<int:eventFrameTemplateId>/<string:activeSourceEventFramesOnly>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def getSourceEventFrames(eventFrameTemplateId, activeSourceEventFramesOnly):
	sourceEventFrames = []

	# Build base query in order to add optional filters.
	query = db.session.query(EventFrame)
	# Optional filters.
	if activeSourceEventFramesOnly == "true":
		query = query.filter_by(EndTimestamp = None)

	# If no event frame template filter is selected, use qualified names for event frame choices.
	if eventFrameTemplateId == 0:
		for eventFrame in query.all():
			sourceEventFrames.append({"value": eventFrame.EventFrameId, "name": eventFrame.fullyQualifiedName()})
	else:
		eventFrameTemplate = EventFrameTemplate.query.get_or_404(eventFrameTemplateId)
		for eventFrame in query.filter_by(EventFrameTemplateId = eventFrameTemplate.EventFrameTemplateId).all():
			sourceEventFrames.append({"value": eventFrame.EventFrameId, "name": eventFrame.Name})

	# Key function used to sort the list of choices.
	def eventFrameName(eventFrame):
		return eventFrame["name"]

	sourceEventFrames = sorted(sourceEventFrames, key = eventFrameName)	
	return jsonify(sourceEventFrames)

@eventFrames.route("/eventFrames/restartEventFrame/<int:eventFrameId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def restartEventFrame(eventFrameId):
	eventFrame = EventFrame.query.get_or_404(eventFrameId)
	eventFrame.restart()
	db.session.commit()
	flash('You have successfully restarted "{}" event frame "{}".'.format(eventFrame.EventFrameTemplate.Name, eventFrame.Name),
		"alert alert-success")
	return redirect(request.referrer)

@eventFrames.route("/eventFrames/select", methods = ["GET", "POST"]) # Default.
@eventFrames.route("/eventFrames/select/<string:selectedClass>", methods = ["GET", "POST"]) # Root.
@eventFrames.route("/eventFrames/select/<string:selectedClass>/<int:selectedId>", methods = ["GET", "POST"])
@eventFrames.route("/eventFrames/select/<string:selectedClass>/<int:selectedId>/<int:months>", methods = ["GET", "POST"])
@eventFrames.route("/eventFrames/select/<string:selectedClass>/<int:selectedId>/<string:selectedOperation>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def selectEventFrame(selectedClass = None, selectedId = None, months = None, selectedOperation = None):
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
	elif selectedClass == "EventFrameTemplate" and selectedOperation == "configure":
		parent = EventFrameTemplate.query.get_or_404(selectedId)
		children = EventFrameTemplate.query.filter_by(ParentEventFrameTemplateId = selectedId).order_by(EventFrameTemplate.Order)
		childrenClass = "DescendantEventFrameTemplate"
		eventFrameAttributeTemplates = EventFrameAttributeTemplate.query.filter_by(EventFrameTemplateId = selectedId). \
			order_by(EventFrameAttributeTemplate.Name)
	elif selectedClass == "EventFrameTemplate":
		parent = EventFrameTemplate.query.get_or_404(selectedId)
		if months is None:
			# Active event frames only.
			session["eventFrameMonths"] = None
			children = EventFrame.query.filter(EventFrame.EventFrameTemplateId == selectedId, EventFrame.EndTimestamp == None)
		elif months == 0:
			# All event frames.
			session["eventFrameMonths"] = 0
			children = EventFrame.query.filter_by(EventFrameTemplateId = selectedId)
		else:
			session["eventFrameMonths"] = months
			fromTimestamp = datetime.utcnow() - relativedelta(months = months)
			toTimestamp = datetime.utcnow()
			children = EventFrame.query.filter(EventFrame.EventFrameTemplateId == selectedId, EventFrame.StartTimestamp >= fromTimestamp,
				EventFrame.StartTimestamp <= toTimestamp)

		eventFrameAttributeTemplates = EventFrameAttributeTemplate.query.filter_by(EventFrameTemplateId = selectedId).order_by(EventFrameAttributeTemplate.Name)
		children = currentEventFrameAttributeValues(children, selectedId)
		childrenClass = "EventFrame"

	return render_template("eventFrames/select.html", children = children, childrenClass = childrenClass,
		eventFrameAttributeTemplates = eventFrameAttributeTemplates, months = months, parent = parent)
