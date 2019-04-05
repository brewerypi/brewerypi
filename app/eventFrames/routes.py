from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import current_app, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from . import eventFrames
from . forms import EventFrameForm, EventFrameOverlayForm
from . helpers import currentEventFrameAttributeValues
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
		parentEventFrame = EventFrame.query.get_or_404(parentEventFrameId)
		form.element.query = Element.query.join(EventFrame).filter(EventFrame.ElementId == parentEventFrame.origin().ElementId)
		form.eventFrameTemplate.query = EventFrameTemplate.query. \
			filter(EventFrameTemplate.ParentEventFrameTemplateId == parentEventFrame.EventFrameTemplateId).order_by(EventFrameTemplate.Name)
	else:
		eventFrameTemplate = EventFrameTemplate.query.get_or_404(eventFrameTemplateId)
		form.element.query = Element.query.join(ElementTemplate).filter(ElementTemplate.ElementTemplateId == eventFrameTemplate.ElementTemplateId). \
			order_by(Element.Name)
		form.eventFrameTemplate.query = EventFrameTemplate.query.filter_by(EventFrameTemplateId = eventFrameTemplateId)

	# Add a new event frame.
	if form.validate_on_submit():
		if form.endUtcTimestamp.data == "":
			endUtcTimestamp = None
		else:
			endUtcTimestamp = form.endUtcTimestamp.data

		if parentEventFrameId:
			eventFrame = EventFrame(EndTimestamp = endUtcTimestamp, EventFrameTemplate = form.eventFrameTemplate.data,
				Name = form.name.data, ParentEventFrameId = parentEventFrameId, StartTimestamp = form.startUtcTimestamp.data, UserId = current_user.get_id())
		else:
			eventFrame = EventFrame(Element = form.element.data, EndTimestamp = endUtcTimestamp, EventFrameTemplateId = eventFrameTemplateId,
				Name = form.name.data, StartTimestamp = form.startUtcTimestamp.data, UserId = current_user.get_id())

		db.session.add(eventFrame)
		db.session.commit()
		count = 0
		for eventFrameAttributeTemplate in eventFrame.EventFrameTemplate.EventFrameAttributeTemplates:
			if eventFrameAttributeTemplate.DefaultStartValue is not None:
				eventFrameAttribute = EventFrameAttribute.query.filter(EventFrameAttribute.ElementId == eventFrame.origin().ElementId,
					EventFrameAttribute.EventFrameAttributeTemplateId == eventFrameAttributeTemplate.EventFrameAttributeTemplateId).one_or_none()
				if eventFrameAttribute is not None:
					tagValue = TagValue(TagId = eventFrameAttribute.TagId, Timestamp = form.startUtcTimestamp.data, UserId = current_user.get_id()
						Value = eventFrameAttributeTemplate.DefaultStartValue)
					db.session.add(tagValue)
					count = count + 1

		if count > 0:
			db.session.commit()

		flash("You have successfully added a new Event Frame.", "alert alert-success")
		return redirect(form.requestReferrer.data)

	if form.requestReferrer.data is None:
		form.requestReferrer.data = request.referrer

	if parentEventFrameId:
		form.parentEventFrameId.data = parentEventFrameId
		breadcrumbs = [{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
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
				text = eventFrameAncestor.EventFrameTemplate.Name + "&nbsp;&nbsp;/&nbsp;&nbsp;" + eventFrameAncestor.Name
			else:
				text = eventFrameAncestor.Name
			breadcrumbs.append({"url" : url_for("eventFrames.dashboard", eventFrameId = eventFrameAncestor.EventFrameId), "text" : text})

		if parentEventFrame.ParentEventFrameId:
			text = parentEventFrame.EventFrameTemplate.Name + "&nbsp;&nbsp;/&nbsp;&nbsp;" + parentEventFrame.Name
		else:
			text = parentEventFrame.Name
		breadcrumbs.append({"url" : url_for("eventFrames.dashboard", eventFrameId = parentEventFrame.EventFrameId), "text" : text})
	else:
		form.eventFrameTemplateId.data = eventFrameTemplateId
		breadcrumbs = [{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
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

	return render_template("eventFrames/addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

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
	eventFrame.delete()
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

		if form.endUtcTimestamp.data == "":
			eventFrame.EndTimestamp = None
		else:
			eventFrame.EndTimestamp = form.endUtcTimestamp.data

		eventFrame.Name = form.name.data
		eventFrame.StartTimestamp = form.startUtcTimestamp.data
		eventFrame.UserId = current_user.get_id()
		db.session.commit()
		flash("You have successfully edited the Event Frame.", "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to edit an existing event frame.
	if eventFrame.ParentEventFrameId:
		form.eventFrameTemplate.data = eventFrame.EventFrameTemplate
		form.parentEventFrameId.data = eventFrame.ParentEventFrameId
		breadcrumbs = [{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
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
				text = eventFrameAncestor.EventFrameTemplate.Name + "&nbsp;&nbsp;/&nbsp;&nbsp;" + eventFrameAncestor.Name
			else:
				text = eventFrameAncestor.Name
			breadcrumbs.append({"url" : url_for("eventFrames.dashboard", eventFrameId = eventFrameAncestor.EventFrameId), "text" : text})

		if eventFrame.ParentEventFrameId:
			text = eventFrame.EventFrameTemplate.Name + "&nbsp;&nbsp;/&nbsp;&nbsp;" + eventFrame.Name
		else:
			text = eventFrame.Name
		breadcrumbs.append({"url" : None, "text" : text})
	else:
		form.element.data = eventFrame.Element
		form.eventFrameTemplateId.data = eventFrame.EventFrameTemplateId
		breadcrumbs = [{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Enterprise",
				selectedId = eventFrame.EventFrameTemplate.ElementTemplate.Site.Enterprise.EnterpriseId),
				"text" : eventFrame.EventFrameTemplate.ElementTemplate.Site.Enterprise.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Site", selectedId = eventFrame.EventFrameTemplate.ElementTemplate.Site.SiteId),
				"text" : eventFrame.EventFrameTemplate.ElementTemplate.Site.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "ElementTemplate",
				selectedId = eventFrame.EventFrameTemplate.ElementTemplate.ElementTemplateId), "text" : eventFrame.EventFrameTemplate.ElementTemplate.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "EventFrameTemplate",
				selectedId = eventFrame.EventFrameTemplate.EventFrameTemplateId), "text" : eventFrame.EventFrameTemplate.Name},
			{"url" : None, "text" : eventFrame.Name}]	

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
	eventFrame.EndTimestamp = datetime.utcnow()
	eventFrame.UserId = current_user.get_id()
	db.session.commit()
	count = 0
	for eventFrameAttributeTemplate in eventFrame.EventFrameTemplate.EventFrameAttributeTemplates:
		if eventFrameAttributeTemplate.DefaultEndValue is not None:
			eventFrameAttribute = EventFrameAttribute.query.filter(EventFrameAttribute.ElementId == eventFrame.origin().ElementId,
				EventFrameAttribute.EventFrameAttributeTemplateId == eventFrameAttributeTemplate.EventFrameAttributeTemplateId).one_or_none()
			if eventFrameAttribute is not None:
				tagValue = TagValue(TagId = eventFrameAttribute.TagId, Timestamp = eventFrame.EndTimestamp, UserId = current_user.get_id(),
					Value = eventFrameAttributeTemplate.DefaultEndValue)
				db.session.add(tagValue)
				count = count + 1

	if count > 0:
		db.session.commit()
	flash("You have successfully ended \"{}\" for event frame \"{}\".".format(eventFrame.EventFrameTemplate.Name, eventFrame.Name),
		"alert alert-success")
	return redirect(request.referrer)

@eventFrames.route("/eventFrames/overlayBuilder/<int:eventFrameTemplateId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def overlayBuilder(eventFrameTemplateId):
	eventFrameTemplate = EventFrameTemplate.query.get_or_404(eventFrameTemplateId)
	eventFrameAttributeTemplates = EventFrameAttributeTemplate.query.filter_by(EventFrameTemplateId = eventFrameTemplateId)
	form = EventFrameOverlayForm()

	if form.validate_on_submit():
		startTimestamp = datetime.strptime(request.form.get("startUtcTimestamp"), "%Y-%m-%d %H:%M:%S")
		if request.form.get("endUtcTimestamp") == "":
			endTimestamp = datetime.utcnow()
		else:
			endTimestamp = datetime.strptime(endUtcTimestamp, "%Y-%m-%d %H:%M:%S")

		eventFrames = EventFrame.query.filter(EventFrame.EventFrameTemplateId == eventFrameTemplateId, EventFrame.StartTimestamp >= startTimestamp,
			EventFrame.StartTimestamp <= endTimestamp)
		eventFrames = currentEventFrameAttributeValues(eventFrames, eventFrameTemplateId)
		return render_template("eventFrames/overlayBuilder.html", endTimestamp = endTimestamp, eventFrames = eventFrames,
			eventFrameAttributeTemplates = eventFrameAttributeTemplates, eventFrameTemplate = eventFrameTemplate,
			grafanaBaseUri = current_app.config["GRAFANA_BASE_URI"], startTimestamp = startTimestamp)

	return render_template("eventFrames/overlayBuilder.html", eventFrameAttributeTemplates = eventFrameAttributeTemplates, eventFrameTemplate = eventFrameTemplate,
		form = form)

@eventFrames.route("/eventFrames/overlay/days", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def days():
	data = request.get_json(force = True)
	eventFrameIds = ""
	for item in data:
		if eventFrameIds != "":
			eventFrameIds = eventFrameIds + ", "
		eventFrameIds = eventFrameIds +  item["EventFrameId"]

	query = """
	SELECT CEILING(IF(EventFrame.EndTimestamp IS NULL,
		(UNIX_TIMESTAMP(TagValue.Timestamp) - UNIX_TIMESTAMP(EventFrame.StartTimestamp)) / 86400,
		(UNIX_TIMESTAMP(EventFrame.EndTimestamp) - UNIX_TIMESTAMP(EventFrame.StartTimestamp)) / 86400)) AS Days
	FROM EventFrame
		INNER JOIN Element ON EventFrame.ElementId = Element.ElementId
		INNER JOIN EventFrameTemplate ON EventFrame.EventFrameTemplateId = EventFrameTemplate.EventFrameTemplateId
		INNER JOIN EventFrameAttributeTemplate ON EventFrameTemplate.EventFrameTemplateId = EventFrameAttributeTemplate.EventFrameTemplateId
		LEFT JOIN EventFrameAttribute ON EventFrameAttributeTemplate.EventFrameAttributeTemplateId = EventFrameAttribute.EventFrameAttributeTemplateId AND
			Element.ElementId = EventFrameAttribute.ElementId
		INNER JOIN
		(
			SELECT EventFrame.EventFrameId AS EventFrameId,
				EventFrameAttributeTemplate.Name AS EventFrameAttributeTemplateName,
				MAX(TagValue.Timestamp) AS Timestamp
			FROM EventFrame
				INNER JOIN Element ON EventFrame.ElementId = Element.ElementId
				INNER JOIN EventFrameTemplate ON EventFrame.EventFrameTemplateId = EventFrameTemplate.EventFrameTemplateId
				INNER JOIN EventFrameAttributeTemplate ON EventFrameTemplate.EventFrameTemplateId = EventFrameAttributeTemplate.EventFrameTemplateId
				LEFT JOIN EventFrameAttribute ON EventFrameAttributeTemplate.EventFrameAttributeTemplateId = EventFrameAttribute.EventFrameAttributeTemplateId AND
					Element.ElementId = EventFrameAttribute.ElementId
				LEFT JOIN Tag ON EventFrameAttribute.TagId = Tag.TagId
				LEFT JOIN TagValue ON Tag.TagId = TagValue.TagId AND
					CASE
						WHEN EventFrame.EndTimestamp IS NULL THEN
							(TagValue.Timestamp >= EventFrame.StartTimestamp)
						ELSE
							(TagValue.Timestamp >= EventFrame.StartTimestamp AND TagValue.Timestamp <= EventFrame.EndTimestamp)
					END
			WHERE EventFrame.EventFrameId IN ({})
			GROUP BY EventFrameId,
				EventFrameAttributeTemplateName
		) CurrentEventFrameAttributeValue ON EventFrame.EventFrameId = CurrentEventFrameAttributeValue.EventFrameId AND
			EventFrameAttributeTemplate.Name = CurrentEventFrameAttributeValue.EventFrameAttributeTemplateName
		LEFT JOIN Tag ON EventFrameAttribute.TagId = Tag.TagId
		LEFT JOIN TagValue ON Tag.TagId = TagValue.TagId AND
			TagValue.Timestamp = CurrentEventFrameAttributeValue.Timestamp
		LEFT JOIN Lookup ON Tag.LookupId = Lookup.LookupId
		LEFT JOIN LookupValue ON Lookup.LookupId = LookupValue.LookupId AND
			TagValue.Value = LookupValue.Value
	WHERE EventFrame.EventFrameId IN ({})
	ORDER BY Days DESC
	LIMIT 1
	""".format(eventFrameIds, eventFrameIds)
	days = db.session.execute(query).fetchone()["Days"]
	return jsonify({"days": days})

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
		if months is None:
			months = 3

		fromTimestamp = datetime.utcnow() - relativedelta(months = months)
		toTimestamp = datetime.utcnow()
		if months == 0:
			children = EventFrame.query.filter_by(EventFrameTemplateId = selectedId)
		else:
			children = EventFrame.query.filter(EventFrame.EventFrameTemplateId == selectedId, EventFrame.StartTimestamp >= fromTimestamp,
				EventFrame.StartTimestamp <= toTimestamp)

		eventFrameAttributeTemplates = EventFrameAttributeTemplate.query.filter_by(EventFrameTemplateId = selectedId).order_by(EventFrameAttributeTemplate.Name)
		children = currentEventFrameAttributeValues(children, selectedId)
		childrenClass = "EventFrame"

	return render_template("eventFrames/select.html", children = children, childrenClass = childrenClass,
		eventFrameAttributeTemplates = eventFrameAttributeTemplates, months = months, parent = parent)
