from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from . import eventFrameNotes
from . forms import EventFrameNoteForm
from .. import db
from .. decorators import permissionRequired
from .. models import EventFrame, EventFrameNote, Note, Permission

modelName = "Event Frame Notes"

@eventFrameNotes.route("/eventFrameNotes/add/<int:eventFrameId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def addEventFrameNote(eventFrameId):
	operation = "Add"
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
	eventFrame = EventFrame.query.get_or_404(eventFrameId)
	if eventFrame.ParentEventFrameId:
		breadcrumbs = []
	else:
		breadcrumbs = [{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Enterprise",
				selectedId = eventFrame.EventFrameTemplate.ElementTemplate.Site.Enterprise.EnterpriseId),
				"text" : eventFrame.EventFrameTemplate.ElementTemplate.Site.Enterprise.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Site", selectedId = eventFrame.EventFrameTemplate.ElementTemplate.Site.SiteId),
				"text" : eventFrame.EventFrameTemplate.ElementTemplate.Site.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "ElementTemplate",
				selectedId = eventFrame.EventFrameTemplate.ElementTemplate.ElementTemplateId),
				"text" : eventFrame.EventFrameTemplate.ElementTemplate.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "EventFrameTemplate",
				selectedId = eventFrame.EventFrameTemplate.EventFrameTemplateId), "text" : eventFrame.EventFrameTemplate.Name},
			{"url" : url_for("eventFrames.dashboard", eventFrameId = eventFrame.EventFrameId), "text" : eventFrame.friendlyName()}]

	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@eventFrameNotes.route("/eventFrameNotes/delete/<int:eventFrameId>/<int:noteId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def deleteEventFrameNote(eventFrameId, noteId):
	eventFrameNote = EventFrameNote.query.filter_by(EventFrameId = eventFrameId, NoteId = noteId).first()
	note = Note.query.get_or_404(noteId)
	db.session.delete(eventFrameNote)
	db.session.delete(note)
	db.session.commit()
	flash("You have successfully deleted the event frame note.", "alert alert-success")
	return redirect(request.referrer)

@eventFrameNotes.route("/eventFrameNotes/edit/<int:eventFrameId>/<int:noteId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def editEventFrameNote(eventFrameId, noteId):
	operation = "Edit"
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
	eventFrame = EventFrame.query.get_or_404(eventFrameId)
	if eventFrame.ParentEventFrameId:
		breadcrumbs = []
	else:
		breadcrumbs = [{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Enterprise",
				selectedId = eventFrame.EventFrameTemplate.ElementTemplate.Site.Enterprise.EnterpriseId),
				"text" : eventFrame.EventFrameTemplate.ElementTemplate.Site.Enterprise.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Site", selectedId = eventFrame.EventFrameTemplate.ElementTemplate.Site.SiteId),
				"text" : eventFrame.EventFrameTemplate.ElementTemplate.Site.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "ElementTemplate",
				selectedId = eventFrame.EventFrameTemplate.ElementTemplate.ElementTemplateId),
				"text" : eventFrame.EventFrameTemplate.ElementTemplate.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "EventFrameTemplate",
				selectedId = eventFrame.EventFrameTemplate.EventFrameTemplateId), "text" : eventFrame.EventFrameTemplate.Name},
			{"url" : url_for("eventFrames.dashboard", eventFrameId = eventFrame.EventFrameId), "text" : eventFrame.friendlyName()},
			{"url" : None, "text" : note.Timestamp}]

	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)
