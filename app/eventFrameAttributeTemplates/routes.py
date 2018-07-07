from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from . import eventFrameAttributeTemplates
from . forms import EventFrameAttributeTemplateForm
from .. import db
from .. decorators import adminRequired
from .. models import EventFrameAttributeTemplate, EventFrameTemplate

@eventFrameAttributeTemplates.route("/eventFrameAttributeTemplates/add/eventFrameTemplateId/<int:eventFrameTemplateId>", methods = ["GET", "POST"])
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
		flash("You have successfully added the new event frame attribute template \"" + eventFrameAttributeTemplate.Name + \
			"\" to the event frame template \"" + eventFrameAttributeTemplate.EventFrameTemplate.Name + "\".", "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to add a new event frame attribute template.
	form.requestReferrer.data = request.referrer
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@eventFrameAttributeTemplates.route("/eventFrameAttributeTemplates/delete/eventFrameAttributeTemplateId/<int:eventFrameAttributeTemplateId>",
	methods = ["GET", "POST"])
@login_required
@adminRequired
def deleteEventFrameAttributeTemplate(eventFrameAttributeTemplateId):
	eventFrameAttributeTemplate = EventFrameAttributeTemplate.query.get_or_404(eventFrameAttributeTemplateId)
	eventFrameTemplateId = eventFrameAttributeTemplate.EventFrameTemplate.EventFrameTemplateId
	db.session.delete(eventFrameAttributeTemplate)
	db.session.commit()
	flash("You have successfully deleted the event frame attribute template \"" + eventFrameAttributeTemplate.Name + "\".", "alert alert-success")
	return redirect(request.referrer)

@eventFrameAttributeTemplates.route("/eventFrameAttributeTemplates/edit/eventFrameAttributeTemplateId/<int:eventFrameAttributeTemplateId>",
	methods = ["GET", "POST"])
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
		return redirect(form.requestReferrer.data)

	# Present a form to edit an existing eventFrameAttributeTemplate.
	form.description.data = eventFrameAttributeTemplate.Description
	form.name.data = eventFrameAttributeTemplate.Name
	form.requestReferrer.data = request.referrer
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)
