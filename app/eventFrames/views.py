from flask import flash, redirect, render_template, request, url_for
from . import eventFrames
from . forms import EventFrameForm
from .. import db
from .. models import Enterprise, ElementTemplate, EventFrame, EventFrameTemplate, Site

modelName = "Event Frame"

@eventFrames.route("/eventFrames", methods = ["GET", "POST"])
# @login_required
def listEventFrames():
	# check_admin()
	eventFrames = EventFrame.query.join(EventFrameTemplate, ElementTemplate, Site, Enterprise)\
		.order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, EventFrameTemplate.Name, EventFrame.Name)
	return render_template("eventFrames/eventFrames.html", eventFrames = eventFrames)

@eventFrames.route("/eventFrames/add", methods = ["GET", "POST"])
# @login_required
def addEventFrame():
	# check_admin()

	operation = "Add"
	form = EventFrameForm()

	# Add a new event frame.
	if form.validate_on_submit():
		eventFrame = EventFrame(Description = form.description.data, EndTime = form.endTime.data, EventFrameTemplate = form.eventFrameTemplate.data, \
			Name = form.name.data, Order = form.order.data, ParentEventFrame = form.parentEventFrame.data, StartTime = form.startTime.data)
		db.session.add(eventFrame)
		db.session.commit()
		flash("You have successfully added a new Event Frame.")
		return redirect(url_for("eventFrames.listEventFrames"))

	# Present a form to add a new event frame.
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@eventFrames.route("/eventFrames/delete/<int:eventFrameId>", methods = ["GET", "POST"])
# @login_required
def deleteEventFrame(eventFrameId):
	# check_admin()
	eventFrame = EventFrame.query.get_or_404(eventFrameId)
	db.session.delete(eventFrame)
	db.session.commit()
	flash("You have successfully deleted the event frame.")
	return redirect(url_for("eventFrames.listEventFrames"))

@eventFrames.route("/eventFrames/edit/<int:eventFrameId>", methods = ["GET", "POST"])
# @login_required
def editEventFrame(eventFrameId):
	# check_admin()
	operation = "Edit"
	eventFrame = EventFrame.query.get_or_404(eventFrameId)
	form = EventFrameForm(obj = eventFrame)

	# Edit an existing event frame.
	if form.validate_on_submit():
		eventFrame.Description = form.description.data
		eventFrame.EndTime = form.endTime.data
		eventFrame.EventFrameTemplate = form.eventFrameTemplate.data
		eventFrame.Name = form.name.data
		eventFrame.Order = form.order.data
		eventFrame.ParentEventFrame = form.parentEventFrame.data
		eventFrame.StartTime = form.startTime.data
		db.session.commit()
		flash("You have successfully edited the Event Frame.")
		return redirect(url_for("eventFrames.listEventFrames"))

	# Present a form to edit an existing event frame template.
	form.description.data = eventFrame.Description
	form.endTime.data = eventFrame.EndTime
	form.eventFrameTemplate.data = eventFrame.EventFrameTemplate
	form.name.data = eventFrame.Name
	form.order.data = eventFrame.Order
	form.parentEventFrame.data = eventFrame.ParentEventFrame
	form.startTime.data = eventFrame.StartTime
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)
