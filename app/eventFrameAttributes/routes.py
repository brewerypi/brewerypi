import csv
import os
from flask import current_app, flash, redirect, render_template, send_file, url_for
from flask_login import login_required
from sqlalchemy import or_
from . import eventFrameAttributes
from . forms import EventFrameAttributeForm, EventFrameAttributeImportForm
from .. import db
from .. decorators import adminRequired, permissionRequired
from .. models import Area, Element, EventFrame, EventFrameAttribute, EventFrameAttributeTemplate, EventFrameTemplate, Enterprise, LookupValue, Permission, Site, Tag, TagValue
from .. tagValues . forms import TagValueForm

@eventFrameAttributes.route("/eventFrameAttributes", methods = ["GET", "POST"])
@login_required
@adminRequired
def listEventFrameAttributes():
	eventFrameAttributes = EventFrameAttribute.query.all()
	return render_template("eventFrameEAttributes/eventFrameAttributes.html", eventFrameEAttributes = eventFrameEAttributes)

@eventFrameAttributes.route("/eventFrameAttributes/add", methods = ["GET", "POST"])
@login_required
@adminRequired
def addEventFrameAttribute():
	modelName = "Event Frame Attribute"
	operation = "Add"
	form = EventFrameAttributeForm()

	# Add a new event frame attribute.
	if form.validate_on_submit():
		eventFrameAttribute = EventFrameAttribute(EventFrameAttributeTemplate = form.eventFrameAttributeTemplate.data, EventFrame = form.eventFrame.data, 
			Tag = form.tag.data)
		db.session.add(eventFrameAttribute)
		db.session.commit()
		flash("You have successfully added the event frame attribute \"" + form.eventFrameAttributeTemplate.data.Name + "\" for \"" + form.eventFrame.data.Name + "\".", "alert alert-success")
		return redirect(url_for("eventFrameAttributes.listEventFrameAttributes"))

	# Present a form to add a new event frame attribute.
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@eventFrameAttributes.route("/eventFrameAttributes/delete/<int:eventFrameAttributeId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def deleteEventFrameAttribute(eventFrameAttributeId):
	eventFrameAttribute = EventFrameAttribute.query.get_or_404(eventFrameAttributeId)
	eventFrameAttributeTemplateName = eventFrameAttribute.EventFrameAttributeTemplate.Name
	eventFrameName = eventFrameAttribute.EventFrame.Name
	db.session.delete(eventFrameAttribute)
	db.session.commit()
	flash("You have successfully deleted the event frame attribute \"" + eventFrameAttributeTemplateName + "\" for \"" + eventFrameName + "\".", "alert alert-success")
	return redirect(url_for("eventFrameAttributes.listEventFrameAttributes"))

@eventFrameAttributes.route("/eventFrameAttributes/edit/<int:eventFrameAttributeId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def editEventFrameAttribute(eventFrameAttributeId):
	modelName = "Event Frame Attribute"
	operation = "Add"
	eventFrameAttribute = EventFrameAttribute.query.get_or_404(eventFrameAttributeId)
	form = EventFrameAttributeForm(obj = eventFrameAttribute)

	# Edit an existing event frame attribute.
	if form.validate_on_submit():	
		eventFrameAttribute.EventFrameAttributeTemplate = form.eventFrameAttributeTemplate.data
		eventFrameAttribute.EventFrame = form.eventFrame.data
		eventFrameAttribute.Tag = form.tag.data
		db.session.commit()
		flash("You have successfully edited the event frame attribute \"" + eventFrameAttribute.EventFrameAttributeTemplate.Name + "\" for \"" + eventFrameAttribute.EventFrame.Name + "\".", "alert alert-success")
		return redirect(url_for("eventFrameAttributes.listEventFrameAttributes"))

	# Present a form to edit an existing event frame attribute.
	form.eventFrameAttributeTemplate.data = eventFrameAttribute.EventFrameAttributeTemplate
	form.eventFrame.data = eventFrameAttribute.EventFrame
	form.tag.data = eventFrameAttribute.Tag
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)
