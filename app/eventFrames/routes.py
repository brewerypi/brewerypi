from flask import flash, redirect, render_template, request, url_for
from . import eventFrames
from . forms import EventFrameForm
from .. import db
from .. models import Enterprise, Element, ElementTemplate, EventFrame, EventFrameTemplate, Site

modelName = "Event Frame"

@eventFrames.route("/eventFrames/<int:parentEventFrameId>", methods = ["GET", "POST"])
@eventFrames.route("/eventFrames/<int:elementId>/<int:eventFrameTemplateId>", methods = ["GET", "POST"])
# @login_required
def listEventFrames(elementId = None, eventFrameTemplateId = None, parentEventFrameId = None):
	# check_admin()
	if parentEventFrameId:
		parentEventFrame = EventFrame.query.get_or_404(parentEventFrameId)
		origin = parentEventFrame.origin()
		element = Element.query.get_or_404(origin.ElementId)
		eventFrameTemplate = EventFrameTemplate.query.get_or_404(parentEventFrame.EventFrameTemplateId)
		eventFrames = EventFrame.query.filter_by(ParentEventFrameId = parentEventFrameId).order_by(EventFrame.StartTimestamp.desc())
	else:
		parentEventFrame = None
		element = Element.query.get_or_404(elementId)
		eventFrameTemplate = EventFrameTemplate.query.get_or_404(eventFrameTemplateId)
		eventFrames = EventFrame.query.filter(EventFrame.ElementId == elementId, EventFrame.EventFrameTemplateId == eventFrameTemplate.EventFrameTemplateId). \
			order_by(EventFrame.StartTimestamp.desc())
	return render_template("eventFrames/eventFrames.html", element = element, eventFrames = eventFrames, eventFrameTemplate = eventFrameTemplate,
		parentEventFrame = parentEventFrame)

@eventFrames.route("/eventFrames/add/<int:elementId>/<int:eventFrameTemplateId>", methods = ["GET", "POST"])
# @login_required
def addEventFrame(elementId, eventFrameTemplateId):
	# check_admin()
	operation = "Add"
	form = EventFrameForm()

	# Add a new event frame.
	if form.validate_on_submit():
		eventFrame = EventFrame(ElementId = form.elementId.data, EndTimestamp = form.endTimestamp.data, EventFrameTemplateId = form.eventFrameTemplateId.data,
			Name = None, ParentEventFrameId = None, StartTimestamp = form.startTimestamp.data)
		db.session.add(eventFrame)
		db.session.commit()
		flash("You have successfully added a new Event Frame.")
		# return redirect(url_for("eventFrames.listEventFrames"))
		return redirect(form.requestReferrer.data)

	# Present a form to add a new event frame.
	form.elementId.data = elementId
	form.eventFrameTemplateId.data = eventFrameTemplateId
	form.requestReferrer.data = request.referrer
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@eventFrames.route("/eventFrames/delete/<int:eventFrameId>", methods = ["GET", "POST"])
# @login_required
def deleteEventFrame(eventFrameId):
	# check_admin()
	eventFrame = EventFrame.query.get_or_404(eventFrameId)
	elementId = eventFrame.ElementId
	db.session.delete(eventFrame)
	db.session.commit()
	flash("You have successfully deleted the event frame.")
	# return redirect(url_for("elements.dashboard", elementId = ElementTemplate))
	return redirect(request.referrer)

@eventFrames.route("/eventFrames/edit/<int:eventFrameId>", methods = ["GET", "POST"])
# @login_required
def editEventFrame(eventFrameId):
	# check_admin()
	operation = "Edit"
	eventFrame = EventFrame.query.get_or_404(eventFrameId)
	form = EventFrameForm(obj = eventFrame)

	# Edit an existing event frame.
	if form.validate_on_submit():
		eventFrame.ElementId = form.elementId.data
		eventFrame.EndTimestamp = form.endTimestamp.data
		eventFrame.EventFrameTemplateId = form.eventFrameTemplateId.data
		# eventFrame.Name = form.name.data
		# eventFrame.ParentEventFrame = form.parentEventFrame.data
		eventFrame.StartTimestamp = form.startTimestamp.data
		db.session.commit()
		flash("You have successfully edited the Event Frame.")
		# return redirect(url_for("elements.dashboard", elementId = eventFrame.ElementId))
		return redirect(form.requestReferrer.data)

	# Present a form to edit an existing event frame.
	form.elementId.data = eventFrame.ElementId
	form.endTimestamp.data = eventFrame.EndTimestamp
	form.eventFrameTemplateId.data = eventFrame.EventFrameTemplateId
	# form.name.data = eventFrame.Name
	# form.parentEventFrame.data = eventFrame.ParentEventFrame
	form.startTimestamp.data = eventFrame.StartTimestamp
	form.requestReferrer.data = request.referrer
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)
