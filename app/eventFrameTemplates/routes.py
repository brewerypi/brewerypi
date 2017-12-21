from flask import flash, redirect, render_template, request, url_for
from . import eventFrameTemplates
from . forms import EventFrameTemplateForm
from .. import db
from .. models import ElementTemplate, EventFrameTemplate, Site, Enterprise

modelName = "Event Frame Templates"

@eventFrameTemplates.route("/eventFrameTemplates", methods = ["GET", "POST"])
# @login_required
def listEventFrameTemplates():
	# check_admin()
	eventFrameTemplates = EventFrameTemplate.query.join(ElementTemplate, Site, Enterprise). \
		order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, EventFrameTemplate.Name)
	return render_template("eventFrameTemplates/eventFrameTemplates.html", eventFrameTemplates = eventFrameTemplates)

@eventFrameTemplates.route("/eventFrameTemplates/add", methods = ["GET", "POST"])
# @login_required
def addEventFrameTemplate():
	# check_admin()
	operation = "Add"
	form = EventFrameTemplateForm()

	# Add a new event frame template.
	if form.validate_on_submit():
		eventFrameTemplate = EventFrameTemplate(Description = form.description.data, ElementTemplate = form.elementTemplate.data, Name = form.name.data, \
			ParentEventFrameTemplate = form.parentEventFrameTemplate.data)
		db.session.add(eventFrameTemplate)
		db.session.commit()
		flash("You have successfully added the event frame template \"" + eventFrameTemplate.Name + "\" to \"" + eventFrameTemplate.ElementTemplate.Name + "\".")
		return redirect(url_for("eventFrameTemplates.listEventFrameTemplates"))

	# Present a form to add a new event frame template.
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
	return redirect(url_for("eventFrameTemplates.listEventFrameTemplates"))

@eventFrameTemplates.route("/eventFrameTemplates/edit/<int:eventFrameTemplateId>", methods = ["GET", "POST"])
# @login_required
def editEventFrameTemplate(eventFrameTemplateId):
	# check_admin()
	operation = "Edit"
	eventFrameTemplate = EventFrameTemplate.query.get_or_404(eventFrameTemplateId)
	form = EventFrameTemplateForm(obj = eventFrameTemplate)

	# Edit an existing event frame template.
	if form.validate_on_submit():
		eventFrameTemplate.Description = form.description.data
		eventFrameTemplate.ElementTemplate = form.elementTemplate.data
		eventFrameTemplate.Name = form.name.data
		eventFrameTemplate.ParentEventFrameTemplate = form.parentEventFrameTemplate.data
		db.session.commit()
		flash("You have successfully edited the event frame template \"" + eventFrameTemplate.Name + "\" for \"" +
			eventFrameTemplate.ElementTemplate.Name + "\".")
		return redirect(url_for("eventFrameTemplates.listEventFrameTemplates"))

	# Present a form to edit an existing event frame template.
	form.description.data = eventFrameTemplate.Description
	form.elementTemplate.data = eventFrameTemplate.ElementTemplate
	form.name.data = eventFrameTemplate.Name
	form.parentEventFrameTemplate.data = eventFrameTemplate.ParentEventFrameTemplate
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)
