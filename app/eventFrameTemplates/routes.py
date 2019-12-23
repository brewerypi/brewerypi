from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from . import eventFrameTemplates
from . forms import CopyEventFrameTemplateForm, EventFrameTemplateForm
from .. import db
from .. decorators import adminRequired
from .. models import ElementTemplate, Enterprise, EventFrameAttribute, EventFrameAttributeTemplate, EventFrameTemplate, Site

modelName = "Event Frame Template"

@eventFrameTemplates.route("/eventFrameTemplates/add/<int:elementTemplateId>", methods = ["GET", "POST"])
@eventFrameTemplates.route("/eventFrameTemplates/add/child/<int:parentEventFrameTemplateId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def addEventFrameTemplate(elementTemplateId = None, parentEventFrameTemplateId = None):
	operation = "Add"
	form = EventFrameTemplateForm()

	if parentEventFrameTemplateId == None:
		del form.order

	# Add a new event frame template.
	if form.validate_on_submit():
		if elementTemplateId:
			eventFrameTemplate = EventFrameTemplate(Description = form.description.data, ElementTemplateId = elementTemplateId,
				Name = form.name.data, Order = 1, ParentEventFrameTemplateId = None)
		else:
			eventFrameTemplate = EventFrameTemplate(Description = form.description.data, ElementTemplateId = None,
				Name = form.name.data, Order = form.order.data, ParentEventFrameTemplateId = parentEventFrameTemplateId)			

		db.session.add(eventFrameTemplate)
		db.session.commit()

		if parentEventFrameTemplateId:
			flash("You have successfully added the event frame template \"" + eventFrameTemplate.Name + "\" to \"" +
				eventFrameTemplate.ParentEventFrameTemplate.Name + "\".", "alert alert-success")
		else:
			flash("You have successfully added the event frame template \"" + eventFrameTemplate.Name + "\" to \"" +
				eventFrameTemplate.ElementTemplate.Name + "\".", "alert alert-success")
			
		return redirect(form.requestReferrer.data)

	# Present a form to add a new event frame template.
	form.elementTemplateId.data = elementTemplateId
	form.parentEventFrameTemplateId.data = parentEventFrameTemplateId
	if parentEventFrameTemplateId:
		childEventFrameTemplateMaximumOrder = EventFrameTemplate.query.filter_by(ParentEventFrameTemplateId = parentEventFrameTemplateId). \
			order_by(EventFrameTemplate.Order.desc()).first()

		if childEventFrameTemplateMaximumOrder:
			nextOrder = childEventFrameTemplateMaximumOrder.Order + 1
		else:
			nextOrder = 1

		form.order.data = nextOrder
		parentEventFrameTemplate = EventFrameTemplate.query.get_or_404(parentEventFrameTemplateId)
		breadcrumbs = [{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Enterprise",
				selectedId = parentEventFrameTemplate.origin().ElementTemplate.Site.Enterprise.EnterpriseId),
				"text" : parentEventFrameTemplate.origin().ElementTemplate.Site.Enterprise.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Site",
				selectedId = parentEventFrameTemplate.origin().ElementTemplate.Site.SiteId),
				"text" : parentEventFrameTemplate.origin().ElementTemplate.Site.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "ElementTemplate",
				selectedId = parentEventFrameTemplate.origin().ElementTemplate.ElementTemplateId),
				"text" : parentEventFrameTemplate.origin().ElementTemplate.Name}]
		for parentEventFrameTemplateAcestor in parentEventFrameTemplate.ancestors([]):
			breadcrumbs.append({"url" : url_for("eventFrames.selectEventFrame", selectedClass = "EventFrameTemplate",
				selectedId = parentEventFrameTemplateAcestor.EventFrameTemplateId, selectedOperation = "configure"),
				"text" : parentEventFrameTemplateAcestor.Name})

		breadcrumbs.append({"url" : url_for("eventFrames.selectEventFrame", selectedClass = "EventFrameTemplate",
			selectedId = parentEventFrameTemplate.EventFrameTemplateId, selectedOperation = "configure"), "text" : parentEventFrameTemplate.Name})
	else:
		elementTemplate = ElementTemplate.query.get_or_404(elementTemplateId)
		breadcrumbs = [{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Enterprise",
				selectedId = elementTemplate.Site.Enterprise.EnterpriseId), "text" : elementTemplate.Site.Enterprise.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Site", selectedId = elementTemplate.Site.SiteId),
				"text" : elementTemplate.Site.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "ElementTemplate", selectedId = elementTemplate.ElementTemplateId),
				"text" : elementTemplate.Name}]

	if form.requestReferrer.data is None:
		form.requestReferrer.data = request.referrer

	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@eventFrameTemplates.route("/eventFrameTemplates/copy/<int:fromEventFrameTemplateId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def copy(fromEventFrameTemplateId):
	operation = "Copy"
	form = CopyEventFrameTemplateForm()
	fromEventFrameTemplate = EventFrameTemplate.query.get_or_404(fromEventFrameTemplateId)
	form.toElementTemplate.choices = [(elementTemplate.ElementTemplateId,
		"{}_{}_{}".format(elementTemplate.Site.Enterprise.Abbreviation, elementTemplate.Site.Abbreviation, elementTemplate.Name)) for elementTemplate in
		ElementTemplate.query.join(Site, Enterprise). \
		filter(ElementTemplate.ElementTemplateId != fromEventFrameTemplate.ElementTemplate.ElementTemplateId). \
		order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name)]

	if form.validate_on_submit():
		toEventFrameTemplate = None
		toParentEventFrameTemplate = None
		previousLevel = None
		for linealDescent in fromEventFrameTemplate.lineage([], 0):
			fromEventFrameTemplate = linealDescent["eventFrameTemplate"]
			fromEventFrameTemplateLevel = linealDescent["level"]
			if fromEventFrameTemplateLevel == 0:
				toEventFrameTemplate = EventFrameTemplate(Description = fromEventFrameTemplate.Description, ElementTemplateId = form.toElementTemplate.data,
					Name = fromEventFrameTemplate.Name, Order = fromEventFrameTemplate.Order, ParentEventFrameTemplate = None)
			else:
				if previousLevel != fromEventFrameTemplateLevel:
					toParentEventFrameTemplate = toEventFrameTemplate

				toEventFrameTemplate = EventFrameTemplate(Description = fromEventFrameTemplate.Description, ElementTemplateId = None,
					Name = fromEventFrameTemplate.Name, Order = fromEventFrameTemplate.Order, ParentEventFrameTemplate = toParentEventFrameTemplate)

			db.session.add(toEventFrameTemplate)
			db.session.commit()
			for fromEventFrameAttributeTemplate in fromEventFrameTemplate.EventFrameAttributeTemplates:
				toEventFrameAttributeTemplate = EventFrameAttributeTemplate(Description = fromEventFrameAttributeTemplate.Description,
					DefaultEndValue = fromEventFrameAttributeTemplate.DefaultEndValue, DefaultStartValue = fromEventFrameAttributeTemplate.DefaultStartValue,
					EventFrameTemplate = toEventFrameTemplate, LookupId = fromEventFrameAttributeTemplate.LookupId,
					Name = fromEventFrameAttributeTemplate.Name, UnitOfMeasurementId = fromEventFrameAttributeTemplate.UnitOfMeasurementId)
				db.session.add(toEventFrameAttributeTemplate)
				db.session.commit()
				toEventFrameAttributeTemplate.postAddHousekeeping(toEventFrameTemplate)

			previousLevel = fromEventFrameTemplateLevel

		return redirect(form.requestReferrer.data)

	# Present a form to copy an event frame template.
	form.name.data = fromEventFrameTemplate.Name
	form.description.data = fromEventFrameTemplate.Description
	breadcrumbs = [{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
		{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Enterprise",
			selectedId = fromEventFrameTemplate.ElementTemplate.Site.Enterprise.EnterpriseId),
			"text" : fromEventFrameTemplate.ElementTemplate.Site.Enterprise.Name},
		{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Site",
			selectedId = fromEventFrameTemplate.ElementTemplate.Site.SiteId), "text" : fromEventFrameTemplate.ElementTemplate.Site.Name},
		{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "ElementTemplate",
			selectedId = fromEventFrameTemplate.ElementTemplate.ElementTemplateId), "text" : fromEventFrameTemplate.ElementTemplate.Name},
		{"url" : None, "text" : fromEventFrameTemplate.Name}]
	if form.requestReferrer.data is None:
		form.requestReferrer.data = request.referrer

	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@eventFrameTemplates.route("/eventFrameTemplates/delete/<int:eventFrameTemplateId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def deleteEventFrameTemplate(eventFrameTemplateId):
	eventFrameTemplate = EventFrameTemplate.query.get_or_404(eventFrameTemplateId)
	eventFrameTemplate.delete()
	db.session.commit()
	flash('You have successfully deleted the event frame template "{}".'.format(eventFrameTemplate.Name), "alert alert-success")

	return redirect(request.referrer)

@eventFrameTemplates.route("/eventFrameTemplates/edit/<int:eventFrameTemplateId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def editEventFrameTemplate(eventFrameTemplateId):
	operation = "Edit"
	eventFrameTemplate = EventFrameTemplate.query.get_or_404(eventFrameTemplateId)
	form = EventFrameTemplateForm(obj = eventFrameTemplate)

	if eventFrameTemplate.ParentEventFrameTemplateId is None:
		del form.order

	# Edit an existing event frame template.
	if form.validate_on_submit():
		if eventFrameTemplate.ParentEventFrameTemplateId is None:
			eventFrameTemplate.ElementTemplateId = form.elementTemplateId.data
			eventFrameTemplate.Order = 1
			eventFrameTemplate.ParentEventFrameTemplateId = None
		else:
			eventFrameTemplate.ElementTemplateId = None
			eventFrameTemplate.Order = form.order.data
			eventFrameTemplate.ParentEventFrameTemplateId = form.parentEventFrameTemplateId.data

		eventFrameTemplate.Description = form.description.data
		eventFrameTemplate.Name = form.name.data
		db.session.commit()

		if eventFrameTemplate.ParentEventFrameTemplateId:
			flash("You have successfully edited the event frame template \"" + eventFrameTemplate.Name + "\" for \"" +
				eventFrameTemplate.ParentEventFrameTemplate.Name + "\".", "alert alert-success")
		else:
			flash("You have successfully edited the event frame template \"" + eventFrameTemplate.Name + "\" for \"" +
				eventFrameTemplate.ElementTemplate.Name + "\".", "alert alert-success")
			
		return redirect(form.requestReferrer.data)

	# Present a form to edit an existing event frame template.
	if eventFrameTemplate.hasParent():
		form.order.data = eventFrameTemplate.Order

		breadcrumbs = [{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Enterprise",
				selectedId = eventFrameTemplate.origin().ElementTemplate.Site.Enterprise.EnterpriseId),
				"text" : eventFrameTemplate.origin().ElementTemplate.Site.Enterprise.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Site",
				selectedId = eventFrameTemplate.origin().ElementTemplate.Site.SiteId),
				"text" : eventFrameTemplate.origin().ElementTemplate.Site.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "ElementTemplate",
				selectedId = eventFrameTemplate.origin().ElementTemplate.ElementTemplateId),
				"text" : eventFrameTemplate.origin().ElementTemplate.Name}]
		for eventFrameTemplateAcestor in eventFrameTemplate.ancestors([]):
			breadcrumbs.append({"url" : url_for("eventFrames.selectEventFrame", selectedClass = "EventFrameTemplate",
				selectedId = eventFrameTemplateAcestor.EventFrameTemplateId, selectedOperation = "configure"), "text" : eventFrameTemplateAcestor.Name})

		breadcrumbs.append({"url" : None, "text" : eventFrameTemplate.Name})
	else:
		breadcrumbs = [{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Enterprise",
				selectedId = eventFrameTemplate.ElementTemplate.Site.Enterprise.EnterpriseId),
				"text" : eventFrameTemplate.ElementTemplate.Site.Enterprise.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Site",
				selectedId = eventFrameTemplate.ElementTemplate.Site.SiteId), "text" : eventFrameTemplate.ElementTemplate.Site.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "ElementTemplate",
				selectedId = eventFrameTemplate.ElementTemplate.ElementTemplateId), "text" : eventFrameTemplate.ElementTemplate.Name},
			{"url" : None, "text" : eventFrameTemplate.Name}]

	form.eventFrameTemplateId.data = eventFrameTemplate.EventFrameTemplateId
	form.description.data = eventFrameTemplate.Description
	form.elementTemplateId.data = eventFrameTemplate.ElementTemplateId
	form.name.data = eventFrameTemplate.Name
	form.parentEventFrameTemplateId.data = eventFrameTemplate.ParentEventFrameTemplateId
	if form.requestReferrer.data is None:
		form.requestReferrer.data = request.referrer

	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)
