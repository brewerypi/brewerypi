from datetime import datetime
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from . import eventFrames
from . forms import EventFrameForm, EventFrameNoteForm
from .. import db
from .. decorators import permissionRequired
from .. models import Element, ElementTemplate, Enterprise, EventFrame, EventFrameAttributeTemplate, EventFrameNote, EventFrameTemplate, Note, Permission, Site

modelName = "Event Frame"

@eventFrames.route("/eventFrames/<int:parentEventFrameId>", methods = ["GET", "POST"])
@eventFrames.route("/eventFrames/<int:elementId>/<int:eventFrameTemplateId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def listEventFrames(elementId = None, eventFrameTemplateId = None, parentEventFrameId = None):
	if parentEventFrameId:
		parentEventFrame = EventFrame.query.get_or_404(parentEventFrameId)
		origin = parentEventFrame.origin()
		element = Element.query.get_or_404(origin.ElementId)
		eventFrameTemplate = EventFrameTemplate.query.get_or_404(parentEventFrame.EventFrameTemplateId)
		eventFrames = EventFrame.query.filter_by(ParentEventFrameId = parentEventFrameId)
	else:
		parentEventFrame = None
		element = Element.query.get_or_404(elementId)
		eventFrameTemplate = EventFrameTemplate.query.get_or_404(eventFrameTemplateId)
		eventFrames = EventFrame.query.filter(EventFrame.ElementId == elementId, EventFrame.EventFrameTemplateId == eventFrameTemplate.EventFrameTemplateId)
	return render_template("eventFrames/eventFrames.html", element = element, eventFrames = eventFrames, eventFrameTemplate = eventFrameTemplate,
		parentEventFrame = parentEventFrame)

@eventFrames.route("/eventFrames/add/<int:parentEventFrameId>", methods = ["GET", "POST"])
@eventFrames.route("/eventFrames/add/<int:elementId>/<int:eventFrameTemplateId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def addEventFrame(elementId = None, eventFrameTemplateId = None, parentEventFrameId = None):
	operation = "Add"
	form = EventFrameForm()

	# Configure the form based on if the event frame has a parent.
	if parentEventFrameId:
		parentEventFrame = EventFrame.query.get_or_404(parentEventFrameId)
		form.eventFrameTemplate.choices = [(eventFrameTemplate.EventFrameTemplateId, eventFrameTemplate.Name) \
			for eventFrameTemplate in EventFrameTemplate.query. \
			filter_by(ParentEventFrameTemplateId = parentEventFrame.EventFrameTemplate.EventFrameTemplateId)]
	else:
		del form.eventFrameTemplate

	# Add a new event frame.
	if form.validate_on_submit():
		if parentEventFrameId:
			eventFrame = EventFrame(EndTimestamp = form.endTimestamp.data, EventFrameTemplateId = form.eventFrameTemplate.data,
				ParentEventFrameId = parentEventFrameId, StartTimestamp = form.startTimestamp.data)
		else:
			eventFrame = EventFrame(ElementId = form.elementId.data, EndTimestamp = form.endTimestamp.data,
				EventFrameTemplateId = form.eventFrameTemplateId.data, StartTimestamp = form.startTimestamp.data)

		db.session.add(eventFrame)
		db.session.commit()
		flash("You have successfully added a new Event Frame.", "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to add a new event frame.
	if parentEventFrameId:
		pass
	else:
		form.elementId.data = elementId
		form.eventFrameTemplateId.data = eventFrameTemplateId

	form.requestReferrer.data = request.referrer
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@eventFrames.route("/eventFrames/dashboard/<int:eventFrameId>/<int:selectedEventFrameTemplateId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def dashboard(eventFrameId, selectedEventFrameTemplateId):
	eventFrame = EventFrame.query.get_or_404(eventFrameId)
	selectedEventFrameTemplate = EventFrameTemplate.query.get_or_404(selectedEventFrameTemplateId)
	return render_template("eventFrames/dashboard.html", eventFrame = eventFrame, selectedEventFrameTemplate = selectedEventFrameTemplate)

@eventFrames.route("/eventFrames/delete/<int:eventFrameId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def deleteEventFrame(eventFrameId):
	eventFrame = EventFrame.query.get_or_404(eventFrameId)
	if eventFrame.hasDescendants():
		flash("This event frame contains one or more child event frames and cannot be deleted.", "alert alert-danger")
	else:
		elementId = eventFrame.ElementId
		db.session.delete(eventFrame)
		db.session.commit()
		flash("You have successfully deleted the event frame.", "alert alert-success")
	return redirect(request.referrer)

@eventFrames.route("/eventFrames/edit/<int:eventFrameId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def editEventFrame(eventFrameId):
	operation = "Edit"
	eventFrame = EventFrame.query.get_or_404(eventFrameId)
	form = EventFrameForm(obj = eventFrame)
	del form.eventFrameTemplate

	# Edit an existing event frame.
	if form.validate_on_submit():
		if eventFrame.ParentEventFrameId:
			eventFrame.ParentEventFrameId = form.parentEventFrameId.data
		else:
			eventFrame.ElementId = form.elementId.data

		eventFrame.EndTimestamp = form.endTimestamp.data
		eventFrame.EventFrameTemplateId = form.eventFrameTemplateId.data
		eventFrame.Name = form.name.data
		eventFrame.StartTimestamp = form.startTimestamp.data
		db.session.commit()
		flash("You have successfully edited the Event Frame.", "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to edit an existing event frame.
	if eventFrame.ParentEventFrameId:
		form.parentEventFrameId.data = eventFrame.ParentEventFrameId
	else:
		form.elementId.data = eventFrame.ElementId

	form.endTimestamp.data = eventFrame.EndTimestamp
	form.eventFrameTemplateId.data = eventFrame.EventFrameTemplateId
	form.name.data = eventFrame.Name
	form.startTimestamp.data = eventFrame.StartTimestamp
	form.requestReferrer.data = request.referrer
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@eventFrames.route("/eventFrames/endEventFrame/<int:eventFrameId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def endEventFrame(eventFrameId):
	eventFrame = EventFrame.query.get_or_404(eventFrameId)
	eventFrame.EndTimestamp = datetime.now()
	db.session.commit()
	flash("You have successfully ended \"" + eventFrame.EventFrameTemplate.Name + "\" for element \"" + eventFrame.origin().Element.Name + "\".",
		"alert alert-success")
	return redirect(request.referrer)

@eventFrames.route("/eventFrames/select", methods = ["GET", "POST"]) # Default.
@eventFrames.route("/eventFrames/select/<string:selectedClass>", methods = ["GET", "POST"]) # Root.
@eventFrames.route("/eventFrames/select/<string:selectedClass>/<int:selectedId>", methods = ["GET", "POST"])
@eventFrames.route("/eventFrames/select/<string:selectedClass>/<int:selectedId>/<int:elementId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def selectEventFrame(selectedClass = None, selectedId = None, elementId = None):
	element = None
	if selectedClass == None:
		parent = Site.query.join(Enterprise).order_by(Enterprise.Name).first()
		if parent:
			children = ElementTemplate.query.filter_by(SiteId = parent.id())
		else:
			children = None
		childrenClass = "ElementTemplate"
	elif selectedClass == "Root":
		parent = None
		children = Enterprise.query.order_by(Enterprise.Name)
		childrenClass = "Enterprise"
	elif selectedClass == "Enterprise":
		parent = Enterprise.query.get_or_404(selectedId)
		children = Site.query.filter_by(EnterpriseId = selectedId)
		childrenClass = "Site"
	elif selectedClass == "Site":
		parent = Site.query.get_or_404(selectedId)
		children = ElementTemplate.query.filter_by(SiteId = selectedId)
		childrenClass = "ElementTemplate"
	elif selectedClass == "ElementTemplate":
		parent = ElementTemplate.query.get_or_404(selectedId)
		children = Element.query.filter_by(ElementTemplateId = selectedId)
		childrenClass = "Element"
	elif selectedClass == "Element":
		parent = Element.query.get_or_404(selectedId)
		children = EventFrameTemplate.query.filter_by(ElementTemplateId = parent.ElementTemplate.ElementTemplateId)
		childrenClass = "EventFrameTemplate"
	elif selectedClass == "EventFrame":
		parent = EventFrameTemplate.query.get_or_404(selectedId)
		children = EventFrame.query.filter(EventFrame.ElementId == elementId, EventFrame.EventFrameTemplateId == selectedId). \
			order_by(EventFrame.StartTimestamp.desc())
		childrenClass = "EventFrame"
		element = Element.query.get_or_404(elementId)

	return render_template("eventFrames/select.html", children = children, childrenClass = childrenClass, element = element, parent = parent)

@eventFrames.route("/eventFrames/startEventFrame/<int:elementId>/<int:eventFrameTemplateId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def startEventFrame(elementId, eventFrameTemplateId):
	eventFrame = EventFrame(ElementId = elementId, EndTimestamp = None, EventFrameTemplateId = eventFrameTemplateId, ParentEventFrameId = None,
		StartTimestamp = datetime.now())
	db.session.add(eventFrame)
	db.session.commit()
	flash("You have successfully added a new \"" + eventFrame.EventFrameTemplate.Name + "\" for element \"" + eventFrame.origin().Element.Name + "\".",
		"alert alert-success")
	return redirect(request.referrer)

@eventFrames.route("/eventFrameNotes/add/<int:eventFrameId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def addEventFrameNote(eventFrameId):
	# check_admin()
	operation = "Add"
	modelName = "Event Frame Note"
	form = EventFrameNoteForm()

	# Add a new event frame note.
	if form.validate_on_submit():
		note = Note(Note = form.note.data, Timestamp = form.timestamp.data)
		db.session.add(note)
		db.session.commit()
		eventFrameNote = EventFrameNote(NoteId = note.NoteId, EventFrameId = eventFrameId)
		db.session.add(eventFrameNote)
		db.session.commit()
		flash("You have successfully added a new Event Frame Note.", "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to add a new event frame note.
	form.requestReferrer.data = request.referrer
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@eventFrames.route("/eventFrameNotes/edit/<int:noteId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def editEventFrameNote(noteId):
	# check_admin()
	operation = "Edit"
	modelName = "Event Frame Note"
	note = Note.query.get_or_404(noteId)
	form = EventFrameNoteForm()

	# Edit an existing event frame note.
	if form.validate_on_submit():
		note.Note = form.note.data
		note.Timestamp = form.timestamp.data
		db.session.commit()
		flash("You have successfully edited the Event Frame Note.", "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to edit an existing event frame.
	form.note.data = note.Note
	form.timestamp.data = note.Timestamp
	form.requestReferrer.data = request.referrer
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@eventFrames.route("/eventFrameNotes/delete/<int:eventFrameId>/<int:noteId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def deleteEventFrameNote(eventFrameId, noteId):
	# check_admin()
	eventFrameNote = EventFrameNote.query.filter_by(EventFrameId = eventFrameId, NoteId = noteId).first()
	note = Note.query.get_or_404(noteId)
	db.session.delete(eventFrameNote)
	db.session.delete(note)
	db.session.commit()
	flash("You have successfully deleted the event frame note.", "alert alert-success")
	return redirect(request.referrer)
