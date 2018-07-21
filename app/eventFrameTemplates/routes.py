from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from . import eventFrameTemplates
from . forms import EventFrameTemplateForm
from .. import db
from .. decorators import adminRequired
from .. models import ElementTemplate, EventFrameAttributeTemplate, EventFrameTemplate, Site, Enterprise

modelName = "Event Frame Template"

@eventFrameTemplates.route("/eventFrameTemplates/add/<int:elementTemplateId>", methods = ["GET", "POST"])
@eventFrameTemplates.route("/eventFrameTemplates/add/<int:parentEventFrameTemplateId>", methods = ["GET", "POST"])
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
	if parentEventFrameTemplateId:
		childEventFrameTemplateMaximumOrder = EventFrameTemplate.query.filter_by(ParentEventFrameTemplateId = parentEventFrameTemplateId). \
			order_by(EventFrameTemplate.Order.desc()).first()

		if childEventFrameTemplateMaximumOrder:
			nextOrder = childEventFrameTemplateMaximumOrder.Order + 1
		else:
			nextOrder = 1

		form.order.data = nextOrder

		parentEventFrameTemplate = EventFrameTemplate.query.get_or_404(parentEventFrameTemplateId)
		breadcrumbs = [{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Root"), "text" : ".."},
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
			breadcrumbs.append({"url" : url_for("eventFrameTemplates.selectEventFrameTemplate",
				eventFrameTemplateId = parentEventFrameTemplateAcestor.EventFrameTemplateId), "text" : parentEventFrameTemplateAcestor.Name})

		breadcrumbs.append({"url" : url_for("eventFrameTemplates.selectEventFrameTemplate",
			eventFrameTemplateId = parentEventFrameTemplate.EventFrameTemplateId), "text" : parentEventFrameTemplate.Name})
	else:
		elementTemplate = ElementTemplate.query.get_or_404(elementTemplateId)
		breadcrumbs = [{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Root"), "text" : ".."},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Enterprise",
				selectedId = elementTemplate.Site.Enterprise.EnterpriseId), "text" : elementTemplate.Site.Enterprise.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Site", selectedId = elementTemplate.Site.SiteId),
				"text" : elementTemplate.Site.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "ElementTemplate", selectedId = elementTemplate.ElementTemplateId),
				"text" : elementTemplate.Name}]	
	form.requestReferrer.data = request.referrer
	return render_template("addEditModel.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@eventFrameTemplates.route("/eventFrameTemplates/delete/<int:eventFrameTemplateId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def deleteEventFrameTemplate(eventFrameTemplateId):
	eventFrameTemplate = EventFrameTemplate.query.get_or_404(eventFrameTemplateId)
	if eventFrameTemplate.hasDescendants():
		flash("This event frame contains one or more child event frame templates and cannot be deleted.", "alert alert-danger")
		return redirect(request.referrer)

	if eventFrameTemplate.ParentEventFrameTemplateId:
		parentEventFrameTemplate = EventFrameTemplate.query.get_or_404(eventFrameTemplate.ParentEventFrameTemplateId)
	else:
		elementTemplate = ElementTemplate.query.get_or_404(eventFrameTemplate.ElementTemplateId)

	db.session.delete(eventFrameTemplate)
	db.session.commit()

	if eventFrameTemplate.ParentEventFrameTemplateId:
		flash("You have successfully deleted the event frame template \"" + eventFrameTemplate.Name + "\" from \"" +
			parentEventFrameTemplate.Name + "\".", "alert alert-success")
	else:
		flash("You have successfully deleted the event frame template \"" + eventFrameTemplate.Name + "\" from \"" + elementTemplate.Name + "\".",
			"alert alert-success")

	return redirect(request.referrer)

@eventFrameTemplates.route("/eventFrameTemplates/edit/<int:eventFrameTemplateId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def editEventFrameTemplate(eventFrameTemplateId):
	operation = "Edit"
	eventFrameTemplate = EventFrameTemplate.query.get_or_404(eventFrameTemplateId)
	form = EventFrameTemplateForm(obj = eventFrameTemplate)

	if eventFrameTemplate.ElementTemplateId:
		del form.order

	# Edit an existing event frame template.
	if form.validate_on_submit():
		if eventFrameTemplate.ElementTemplateId:
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
		breadcrumbs = [{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Root"), "text" : ".."},
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
			breadcrumbs.append({"url" : url_for("eventFrameTemplates.selectEventFrameTemplate",
				eventFrameTemplateId = eventFrameTemplateAcestor.EventFrameTemplateId), "text" : eventFrameTemplateAcestor.Name})

		breadcrumbs.append({"url" : None, "text" : eventFrameTemplate.Name})
	else:
		form.elementTemplateId.data = eventFrameTemplate.ElementTemplateId
		breadcrumbs = [{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Root"), "text" : ".."},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Enterprise",
				selectedId = eventFrameTemplate.ElementTemplate.Site.Enterprise.EnterpriseId),
				"text" : eventFrameTemplate.ElementTemplate.Site.Enterprise.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Site",
				selectedId = eventFrameTemplate.ElementTemplate.Site.SiteId), "text" : eventFrameTemplate.ElementTemplate.Site.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "ElementTemplate",
				selectedId = eventFrameTemplate.ElementTemplate.ElementTemplateId), "text" : eventFrameTemplate.ElementTemplate.Name},
			{"url" : None, "text" : eventFrameTemplate.Name}]

	form.description.data = eventFrameTemplate.Description
	form.name.data = eventFrameTemplate.Name
	form.parentEventFrameTemplateId.data = eventFrameTemplate.ParentEventFrameTemplateId
	form.requestReferrer.data = request.referrer
	return render_template("addEditModel.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@eventFrameTemplates.route("/eventFrameTemplates/select/<int:eventFrameTemplateId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def selectEventFrameTemplate(eventFrameTemplateId):
	parent = EventFrameTemplate.query.get_or_404(eventFrameTemplateId)
	children = EventFrameTemplate.query.filter_by(ParentEventFrameTemplateId = eventFrameTemplateId).order_by(EventFrameTemplate.Order)
	childrenClass = "DescendantEventFrameTemplate"
	eventFrameAttributeTemplates = EventFrameAttributeTemplate.query. \
		filter_by(EventFrameTemplateId = eventFrameTemplateId).order_by(EventFrameAttributeTemplate.Name)
	return render_template("eventFrameTemplates/select.html", children = children, childrenClass = childrenClass,
		eventFrameAttributeTemplates = eventFrameAttributeTemplates, parent = parent)
