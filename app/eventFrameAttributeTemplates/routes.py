from flask import flash, redirect, render_template, url_for
from flask_login import login_required
from . import eventFrameAttributeTemplates
from . forms import EventFrameAttributeTemplateForm
from .. import db
from .. decorators import adminRequired
from .. models import EventFrameAttributeTemplate, EventFrameTemplate, ElementTemplate, Enterprise, Site

modelName = "Event Frame Attribute Template"

@eventFrameAttributeTemplates.route("/eventFrameAttributeTemplates", methods = ["GET", "POST"])
@login_required
@adminRequired
def listEventFrameAttributeTemplates():
	eventFrameAttributeTemplates = EventFrameAttributeTemplate.query.all()
	return render_template("eventFrameAttributeTemplates/eventFrameAttributeTemplates.html", eventFrameAttributeTemplates = eventFrameAttributeTemplates)

@eventFrameAttributeTemplates.route("/eventFrameAttributeTemplates/add", methods = ["GET", "POST"])
@login_required
@adminRequired
def addEventFrameAttributeTemplate():
	operation = "Add"
	form = EventFrameAttributeTemplateForm()

	# Add a new eventFrameAttributeTemplate
	if form.validate_on_submit():
		eventFrameAttributeTemplate = EventFrameAttributeTemplate(Description = form.description.data, EventFrameTemplate = form.eventFrameTemplate.data, 
			Name = form.name.data)
		db.session.add(eventFrameAttributeTemplate)
		db.session.commit()
		flash("You have successfully added the new event frame attribute template \"" + eventFrameAttributeTemplate.Name + "\".", "alert alert-success")
		return redirect(url_for("eventFrameAttributeTemplates.listEventFrameAttributeTemplates"))

	# Present a form to add a new event frame attribute template.
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@eventFrameAttributeTemplates.route("/eventFrameAttributeTemplates/delete/<int:eventFrameAttributeTemplateId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def deleteEventFrameAttributeTemplate(eventFrameAttributeTemplateId):
	eventFrameAttributeTemplate = EventFrameAttributeTemplate.query.get_or_404(eventFrameAttributeTemplateId)
	db.session.delete(eventFrameAttributeTemplate)
	db.session.commit()
	flash("You have successfully deleted the event frame attribute template \"" + eventFrameAttributeTemplate.Name + "\".", "alert alert-success")
	return redirect(url_for("eventFrameAttributeTemplates.listEventFrameAttributeTemplates"))

@eventFrameAttributeTemplates.route("/eventFrameAttributeTemplates/edit/<int:eventFrameAttributeTemplateId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def editEventFrameAttributeTemplate(eventFrameAttributeTemplateId):
	operation = "Edit"
	eventFrameAttributeTemplate = EventFrameAttributeTemplate.query.get_or_404(eventFrameAttributeTemplateId)
	form = EventFrameAttributeTemplateForm(obj = eventFrameAttributeTemplate)

	# Edit an existing eventFrameAttributeTemplate.
	if form.validate_on_submit():
		eventFrameAttributeTemplate.Description = form.description.data
		eventFrameAttributeTemplate.EventFrameTemplate = form.eventFrameTemplate.data
		eventFrameAttributeTemplate.Name = form.name.data
		db.session.commit()
		flash("You have successfully edited the event frame attribute template \"" + eventFrameAttributeTemplate.Name + "\".", "alert alert-success")
		return redirect(url_for("eventFrameAttributeTemplates.listEventFrameAttributeTemplates"))

	# Present a form to edit an existing eventFrameAttributeTemplate.
	form.description.data = eventFrameAttributeTemplate.Description
	form.eventFrameTemplate.data = eventFrameAttributeTemplate.EventFrameTemplate
	form.name.data = eventFrameAttributeTemplate.Name
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)
