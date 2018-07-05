from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import text
from sqlalchemy.orm import aliased
from . import eventFrameTemplates
from . forms import EventFrameAttributeTemplateForm, EventFrameTemplateForm
from .. import db
from .. decorators import adminRequired
from .. models import ElementTemplate, EventFrameAttributeTemplate, EventFrameTemplate, Site, Enterprise

@eventFrameTemplates.route("/eventFrameAttributeTemplates/add/eventFrameTemplateId/<int:eventFrameTemplateId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def addEventFrameAttributeTemplate(eventFrameTemplateId):
	modelName = "Event Frame Attribute Template"
	operation = "Add"
	form = EventFrameAttributeTemplateForm()

	# Add a new eventFrameAttributeTemplate
	if form.validate_on_submit():
		eventFrameAttributeTemplate = EventFrameAttributeTemplate(Description = form.description.data, EventFrameTemplateId = eventFrameTemplateId, 
			Name = form.name.data)
		db.session.add(eventFrameAttributeTemplate)
		db.session.commit()
		flash("You have successfully added the new event frame attribute template \"" + eventFrameAttributeTemplate.Name + "\" to the event frame template \"" + eventFrameAttributeTemplate.EventFrameTemplate.Name + "\".", "alert alert-success")
		return redirect(url_for("eventFrameTemplates.select", className = "EventFrameTemplate", id = eventFrameTemplateId))

	# Present a form to add a new event frame attribute template.
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@eventFrameTemplates.route("/eventFrameTemplates/add/elementTemplateId/<int:elementTemplateId>", methods = ["GET", "POST"])
@eventFrameTemplates.route("/eventFrameTemplates/add/eventFrameTemplateId/<int:parentEventFrameTemplateId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def addEventFrameTemplate(elementTemplateId = None, parentEventFrameTemplateId = None):
	modelName = "Event Frame Templates"
	operation = "Add"
	form = EventFrameTemplateForm()

	if elementTemplateId:
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
	form.requestReferrer.data = request.referrer
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@eventFrameTemplates.route("/eventFrameAttributeTemplates/delete/eventFrameAttributeTemplateId/<int:eventFrameAttributeTemplateId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def deleteEventFrameAttributeTemplate(eventFrameAttributeTemplateId):
	eventFrameAttributeTemplate = EventFrameAttributeTemplate.query.get_or_404(eventFrameAttributeTemplateId)
	eventFrameTemplateId = eventFrameAttributeTemplate.EventFrameTemplate.EventFrameTemplateId
	db.session.delete(eventFrameAttributeTemplate)
	db.session.commit()
	flash("You have successfully deleted the event frame attribute template \"" + eventFrameAttributeTemplate.Name + "\".", "alert alert-success")
	return redirect(url_for("eventFrameTemplates.select", className = "EventFrameTemplate", id = eventFrameTemplateId))

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

@eventFrameTemplates.route("/eventFrameAttributeTemplates/edit/eventFrameAttributeTemplateId/<int:eventFrameAttributeTemplateId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def editEventFrameAttributeTemplate(eventFrameAttributeTemplateId):
	modelName = "Event Frame Attribute Template"
	operation = "Edit"
	eventFrameAttributeTemplate = EventFrameAttributeTemplate.query.get_or_404(eventFrameAttributeTemplateId)
	eventFrameTemplateId = eventFrameAttributeTemplate.EventFrameTemplate.EventFrameTemplateId
	form = EventFrameAttributeTemplateForm(obj = eventFrameAttributeTemplate)

	# Edit an existing eventFrameAttributeTemplate.
	if form.validate_on_submit():
		eventFrameAttributeTemplate.Description = form.description.data
		eventFrameAttributeTemplate.Name = form.name.data
		db.session.commit()
		flash("You have successfully edited the event frame attribute template \"" + eventFrameAttributeTemplate.Name + "\".", "alert alert-success")
		return redirect(url_for("eventFrameTemplates.select", className = "EventFrameTemplate", id = eventFrameTemplateId))

	# Present a form to edit an existing eventFrameAttributeTemplate.
	form.description.data = eventFrameAttributeTemplate.Description
	form.name.data = eventFrameAttributeTemplate.Name
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@eventFrameTemplates.route("/eventFrameTemplates/edit/<int:eventFrameTemplateId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def editEventFrameTemplate(eventFrameTemplateId):
	modelName = "Event Frame Templates"
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
	if eventFrameTemplate.ElementTemplateId:
		form.elementTemplateId.data = eventFrameTemplate.ElementTemplateId
	else:
		form.order.data = eventFrameTemplate.Order

	form.description.data = eventFrameTemplate.Description
	form.name.data = eventFrameTemplate.Name
	form.parentEventFrameTemplateId.data = eventFrameTemplate.ParentEventFrameTemplateId
	form.requestReferrer.data = request.referrer
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@eventFrameTemplates.route("/select", methods = ["GET", "POST"])
@eventFrameTemplates.route("/select/<string:className>", methods = ["GET", "POST"])
@eventFrameTemplates.route("/select/<string:className>/<int:id>", methods = ["GET", "POST"])
@login_required
@adminRequired
def select(className = None, id = None):
	eventFrameAttributeTemplates = None
	if className == None:
		parent = Site.query.join(Enterprise).order_by(Enterprise.Name, Site.Name).first()
		if parent:
			children = ElementTemplate.query.join(Site).filter_by(SiteId = parent.id()).order_by(ElementTemplate.Name)
		else:
			children = None
		className = "ElementTemplate"
	elif className == "Root":
		parent = None
		children = Enterprise.query.order_by(Enterprise.Name)
		className = "Enterprise"
	elif className == "Enterprise":
		parent = Enterprise.query.get_or_404(id)
		children = Site.query.join(Enterprise).filter_by(EnterpriseId = id).order_by(Site.Name)
		className = "Site"
	elif className == "Site":
		parent = Site.query.get_or_404(id)
		children = ElementTemplate.query.join(Site).filter_by(SiteId = id).order_by(ElementTemplate.Name)
		className = "ElementTemplate"
	elif className == "ElementTemplate":
		parent = ElementTemplate.query.get_or_404(id)
		children = EventFrameTemplate.query.join(ElementTemplate).filter_by(ElementTemplateId = id).order_by(EventFrameTemplate.Name)
		className = "EventFrameTemplate"
	elif className == "EventFrameTemplate":
		parent = EventFrameTemplate.query.get_or_404(id)
		children = EventFrameTemplate.query.filter_by(ParentEventFrameTemplateId = id).order_by(EventFrameTemplate.Order)
		className = None
		eventFrameAttributeTemplates = EventFrameAttributeTemplate.query.filter_by(EventFrameTemplateId = id).order_by(EventFrameAttributeTemplate.Name)

	return render_template("eventFrameTemplates/select.html", children = children, className = className, eventFrameAttributeTemplates = eventFrameAttributeTemplates, parent = parent)
