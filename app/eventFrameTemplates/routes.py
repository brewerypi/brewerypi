from flask import flash, redirect, render_template, request, url_for
from sqlalchemy.orm import aliased
from . import eventFrameTemplates
from . forms import EventFrameTemplateForm
from .. import db
from .. models import ElementTemplate, EventFrameTemplate, Site, Enterprise

modelName = "Event Frame Templates"

@eventFrameTemplates.route("/eventFrameTemplates", methods = ["GET", "POST"])
@eventFrameTemplates.route("/eventFrameTemplates/<int:parentEventFrameTemplateId>", methods = ["GET", "POST"])
# @login_required
def listEventFrameTemplates(parentEventFrameTemplateId = None):
	# check_admin()
	# parentEventFrameTemplate = aliased(EventFrameTemplate)
	# eventFrameTemplates = EventFrameTemplate.query.join(ElementTemplate, Site, Enterprise). \
	# 	outerjoin(parentEventFrameTemplate, EventFrameTemplate.ParentEventFrameTemplateId == parentEventFrameTemplate.EventFrameTemplateId). \
	# 	order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, parentEventFrameTemplate.Name, EventFrameTemplate.Order)
	parentEventFrameTemplate = None
	if parentEventFrameTemplateId:
		parentEventFrameTemplate = EventFrameTemplate.query.get_or_404(parentEventFrameTemplateId)

	eventFrameTemplates = EventFrameTemplate.query.join(ElementTemplate, Site, Enterprise). \
		filter(EventFrameTemplate.ParentEventFrameTemplateId == parentEventFrameTemplateId). \
		order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, EventFrameTemplate.Order, EventFrameTemplate.Name)
	return render_template("eventFrameTemplates/eventFrameTemplates.html", eventFrameTemplates = eventFrameTemplates,
		parentEventFrameTemplate = parentEventFrameTemplate)

@eventFrameTemplates.route("/eventFrameTemplates/add", methods = ["GET", "POST"])
@eventFrameTemplates.route("/eventFrameTemplates/add/<int:parentEventFrameTemplateId>", methods = ["GET", "POST"])
# @login_required
def addEventFrameTemplate(parentEventFrameTemplateId = None):
	# check_admin()
	operation = "Add"
	form = EventFrameTemplateForm()

	if parentEventFrameTemplateId:
		parentEventFrameTemplate = EventFrameTemplate.query.get_or_404(parentEventFrameTemplateId)
		del form.elementTemplate
	else:
		del form.order

	# Add a new event frame template.
	if form.validate_on_submit():
		if parentEventFrameTemplateId:
			eventFrameTemplate = EventFrameTemplate(Description = form.description.data, ElementTemplateId = parentEventFrameTemplate.ElementTemplateId,
				Name = form.name.data, Order = form.order.data, ParentEventFrameTemplateId = parentEventFrameTemplateId)			
		else:
			eventFrameTemplate = EventFrameTemplate(Description = form.description.data, ElementTemplate = form.elementTemplate.data, Name = form.name.data, \
				Order = 1, ParentEventFrameTemplateId = None)

		db.session.add(eventFrameTemplate)
		db.session.commit()
		flash("You have successfully added the event frame template \"" + eventFrameTemplate.Name + "\" to \"" +
			eventFrameTemplate.ElementTemplate.Name + "\".")
		return redirect(url_for("eventFrameTemplates.listEventFrameTemplates", parentEventFrameTemplateId = parentEventFrameTemplateId))

	# Present a form to add a new event frame template.
	if parentEventFrameTemplateId:
		childEventFrameTemplateMaximumOrder = EventFrameTemplate.query.filter_by(ParentEventFrameTemplateId = parentEventFrameTemplateId). \
			order_by(EventFrameTemplate.Order.desc()).first()

		if childEventFrameTemplateMaximumOrder:
			nextOrder = childEventFrameTemplateMaximumOrder.Order + 1
		else:
			nextOrder = 1

		form.order.data = nextOrder
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@eventFrameTemplates.route("/eventFrameTemplates/delete/<int:eventFrameTemplateId>", methods = ["GET", "POST"])
# @login_required
def deleteEventFrameTemplate(eventFrameTemplateId):
	# check_admin()
	eventFrameTemplate = EventFrameTemplate.query.get_or_404(eventFrameTemplateId)
	elementTemplate = ElementTemplate.query.get_or_404(eventFrameTemplate.ElementTemplateId)
	db.session.delete(eventFrameTemplate)
	db.session.commit()
	flash("You have successfully deleted the event frame template \"" + eventFrameTemplate.Name + "\" from \"" + elementTemplate.Name + "\".")
	return redirect(url_for("eventFrameTemplates.listEventFrameTemplates", parentEventFrameTemplateId = eventFrameTemplate.ParentEventFrameTemplateId))

@eventFrameTemplates.route("/eventFrameTemplates/edit/<int:eventFrameTemplateId>", methods = ["GET", "POST"])
# @login_required
def editEventFrameTemplate(eventFrameTemplateId):
	# check_admin()
	operation = "Edit"
	eventFrameTemplate = EventFrameTemplate.query.get_or_404(eventFrameTemplateId)
	form = EventFrameTemplateForm(obj = eventFrameTemplate)

	if eventFrameTemplate.ParentEventFrameTemplateId:
		del form.elementTemplate
	else:
		del form.order

	# Edit an existing event frame template.
	if form.validate_on_submit():
		if eventFrameTemplate.ParentEventFrameTemplateId:
			eventFrameTemplate.ElementTemplateId = form.elementTemplateId.data
			eventFrameTemplate.Order = form.order.data
			eventFrameTemplate.ParentEventFrameTemplateId = form.parentEventFrameTemplateId.data
		else:
			eventFrameTemplate.ElementTemplate = form.elementTemplate.data
			eventFrameTemplate.Order = 1
			eventFrameTemplate.ParentEventFrameTemplateId = None

		eventFrameTemplate.Description = form.description.data
		eventFrameTemplate.Name = form.name.data
		# eventFrameTemplate.ParentEventFrameTemplate = form.parentEventFrameTemplate.data
		db.session.commit()
		flash("You have successfully edited the event frame template \"" + eventFrameTemplate.Name + "\" for \"" +
			eventFrameTemplate.ElementTemplate.Name + "\".")
		return redirect(url_for("eventFrameTemplates.listEventFrameTemplates", parentEventFrameTemplateId = eventFrameTemplate.ParentEventFrameTemplateId))

	# Present a form to edit an existing event frame template.
	if eventFrameTemplate.ParentEventFrameTemplateId:
		form.elementTemplateId.data = eventFrameTemplate.ElementTemplateId
		form.order.data = eventFrameTemplate.Order
		form.parentEventFrameTemplateId.data = eventFrameTemplate.ParentEventFrameTemplateId
	else:
		form.elementTemplate.data = eventFrameTemplate.ElementTemplate
		# form.order.data = 1
		form.parentEventFrameTemplateId.data = None
		# form.order.data = eventFrameTemplate.Order

	form.description.data = eventFrameTemplate.Description
	# form.elementTemplate.data = eventFrameTemplate.ElementTemplate
	form.name.data = eventFrameTemplate.Name
	# form.order.data = eventFrameTemplate.Order
	# form.parentEventFrameTemplate.data = eventFrameTemplate.ParentEventFrameTemplate
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)
