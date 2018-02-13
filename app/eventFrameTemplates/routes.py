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
	parentEventFrameTemplate = None
	if parentEventFrameTemplateId:
		parentEventFrameTemplate = EventFrameTemplate.query.get_or_404(parentEventFrameTemplateId)

	page = request.args.get("page", 1, type = int)
	pagination = EventFrameTemplate.query.outerjoin(ElementTemplate, Site, Enterprise). \
		filter(EventFrameTemplate.ParentEventFrameTemplateId == parentEventFrameTemplateId). \
		order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, EventFrameTemplate.Order, EventFrameTemplate.Name). \
		paginate(page, per_page = 10, error_out = False)
	eventFrameTemplates = pagination.items
	return render_template("eventFrameTemplates/eventFrameTemplates.html", eventFrameTemplates = eventFrameTemplates,
		pagination = pagination, parentEventFrameTemplate = parentEventFrameTemplate)

@eventFrameTemplates.route("/eventFrameTemplates/add", methods = ["GET", "POST"])
@eventFrameTemplates.route("/eventFrameTemplates/add/<int:parentEventFrameTemplateId>", methods = ["GET", "POST"])
# @login_required
def addEventFrameTemplate(parentEventFrameTemplateId = None):
	# check_admin()
	operation = "Add"
	form = EventFrameTemplateForm()

	if parentEventFrameTemplateId:
		del form.elementTemplate
	else:
		del form.order

	# Add a new event frame template.
	if form.validate_on_submit():
		if parentEventFrameTemplateId:
			eventFrameTemplate = EventFrameTemplate(Description = form.description.data, ElementTemplate = None,
				Name = form.name.data, Order = form.order.data, ParentEventFrameTemplateId = parentEventFrameTemplateId)			
		else:
			eventFrameTemplate = EventFrameTemplate(Description = form.description.data, ElementTemplate = form.elementTemplate.data,
				Name = form.name.data, Order = 1, ParentEventFrameTemplateId = None)

		db.session.add(eventFrameTemplate)
		db.session.commit()

		if parentEventFrameTemplateId:
			flash("You have successfully added the event frame template \"" + eventFrameTemplate.Name + "\" to \"" +
				eventFrameTemplate.ParentEventFrameTemplate.Name + "\".", "alert alert-success")
		else:
			flash("You have successfully added the event frame template \"" + eventFrameTemplate.Name + "\" to \"" +
				eventFrameTemplate.ElementTemplate.Name + "\".", "alert alert-success")
			
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
			eventFrameTemplate.ElementTemplate = None
			eventFrameTemplate.Order = form.order.data
			eventFrameTemplate.ParentEventFrameTemplateId = form.parentEventFrameTemplateId.data
		else:
			eventFrameTemplate.ElementTemplate = form.elementTemplate.data
			eventFrameTemplate.Order = 1
			eventFrameTemplate.ParentEventFrameTemplateId = None

		eventFrameTemplate.Description = form.description.data
		eventFrameTemplate.Name = form.name.data
		db.session.commit()

		if eventFrameTemplate.ParentEventFrameTemplateId:
			flash("You have successfully edited the event frame template \"" + eventFrameTemplate.Name + "\" for \"" +
				eventFrameTemplate.ParentEventFrameTemplate.Name + "\".", "alert alert-success")
		else:
			flash("You have successfully edited the event frame template \"" + eventFrameTemplate.Name + "\" for \"" +
				eventFrameTemplate.ElementTemplate.Name + "\".", "alert alert-success")
			
		return redirect(url_for("eventFrameTemplates.listEventFrameTemplates", parentEventFrameTemplateId = eventFrameTemplate.ParentEventFrameTemplateId))

	# Present a form to edit an existing event frame template.
	if eventFrameTemplate.ParentEventFrameTemplateId:
		form.order.data = eventFrameTemplate.Order
	else:
		form.elementTemplate.data = eventFrameTemplate.ElementTemplate

	form.description.data = eventFrameTemplate.Description
	form.name.data = eventFrameTemplate.Name
	form.parentEventFrameTemplateId.data = eventFrameTemplate.ParentEventFrameTemplateId
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@eventFrameTemplates.route("/selectEventFrameTemplate", methods = ["GET", "POST"])
@eventFrameTemplates.route("/selectEventFrameTemplate/<string:className>", methods = ["GET", "POST"])
@eventFrameTemplates.route("/selectEventFrameTemplate/<string:className>/<int:id>", methods = ["GET", "POST"])
# @login_required
def selectEventFrameTemplate(className = None, id = None):
	# check_admin()
	# elements = None
	elementTemplate = None
	elementTemplates = None
	eventFrameTemplates = None
	# enterprises = None
	# site = None
	# sites = None

	# Default case.
	if className == None:
		# site = Site.query.join(Enterprise).order_by(Enterprise.Name, Site.Name).first()
		# if site:
		# 	className = site.__class__.__name__
		elementTemplate = ElementTemplate.query.join(Site, Enterprise).order_by(Enterprise.Name, Site.Name, ElementTemplate.Name).first()
		if elementTemplate:
			className = elementTemplate.__class__.__name__
	# Top level case.
	# elif className == "root":
	# 	enterprises = Enterprise.query.all()
	# elif className == "Enterprise":
	# 	sites = Site.query.filter_by(EnterpriseId = id)
	# 	if sites:
	# 		className = sites[0].__class__.__name__
	elif className == "Site":
		elementTemplates = ElementTemplate.query.filter_by(SiteId = id)
		if elementTemplates:
			className = elementTemplates[0].__class__.__name__
	elif className == "ElementTemplate":
		eventFrameTemplates = EventFrameTemplate.query.filter_by(EventFrameTemplateId = id)
		if eventFrameTemplates:
			className = eventFrameTemplates[0].__class__.__name__
	# elif className == "Element":
	# 	return redirect(url_for("elements.dashboard", elementId = id))

	# Present navigation for event frames.
	# return render_template("elements/selectEventFrame.html", className = className, elements = elements, elementTemplates = elementTemplates,
	# 	enterprises = enterprises, site = site, sites = sites)
	return render_template("eventFrameTemplates/selectEventFrameTemplate.html", className = className, elementTemplate = elementTemplate,
		elementTemplates = elementTemplates, eventFrameTemplates = eventFrameTemplates)
