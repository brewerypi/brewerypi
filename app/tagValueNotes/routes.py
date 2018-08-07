from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import or_
from . import tagValueNotes
from . forms import TagValueNoteForm
from .. import db
from .. decorators import permissionRequired
from .. models import ElementAttribute, EventFrame, EventFrameAttribute, Note, Permission, TagValue, TagValueNote

modelName = "Tag Value Note"

@tagValueNotes.route("/tagValueNotes/<int:tagValueId>", methods = ["GET", "POST"])
@tagValueNotes.route("/tagValueNotes/<int:tagValueId>/<int:elementAttributeId>", methods = ["GET", "POST"])
@tagValueNotes.route("/tagValueNotes/<int:tagValueId>/<int:eventFrameId>/<int:eventFrameAttributeId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def listTagValueNotes(tagValueId, elementAttributeId = None, eventFrameId = None, eventFrameAttributeId = None):
	elementAttribute = None
	eventFrame = None
	eventFrameAttribute = None
	if elementAttributeId:
		elementAttribute = ElementAttribute.query.get_or_404(elementAttributeId)
	elif eventFrameId:
		eventFrame = EventFrame.query.get_or_404(eventFrameId)
		eventFrameAttribute = EventFrameAttribute.query.get_or_404(eventFrameAttributeId)

	tagValue = TagValue.query.get_or_404(tagValueId)
	tagValueNotes = TagValueNote.query.filter_by(TagValueId = tagValueId)
	return render_template("tagValueNotes/tagValueNotes.html", elementAttribute = elementAttribute, eventFrame = eventFrame,
		eventFrameAttribute = eventFrameAttribute, tagValue = tagValue, tagValueNotes = tagValueNotes)

@tagValueNotes.route("/tagValueNotes/add/<int:tagValueId>", methods = ["GET", "POST"])
@tagValueNotes.route("/tagValueNotes/add/<int:tagValueId>/<int:elementAttributeId>", methods = ["GET", "POST"])
@tagValueNotes.route("/tagValueNotes/add/<int:tagValueId>/<int:eventFrameId>/<int:eventFrameAttributeId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def addTagValueNote(tagValueId, elementAttributeId = None, eventFrameId = None, eventFrameAttributeId = None):
	operation = "Add"
	modelName = "Tag Value Note"
	form = TagValueNoteForm()

	# Add a new tag value note.
	if form.validate_on_submit():
		note = Note(Note = form.note.data, Timestamp = form.timestamp.data)
		db.session.add(note)
		db.session.commit()
		tagValueNote = TagValueNote(NoteId = note.NoteId, TagValueId = tagValueId)
		db.session.add(tagValueNote)
		db.session.commit()
		flash("You have successfully added a new Tag Value Note.", "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to add a new tag value note.
	form.requestReferrer.data = request.referrer
	tagValue = TagValue.query.get_or_404(tagValueId)
	if elementAttributeId:
		elementAttribute = ElementAttribute.query.get_or_404(elementAttributeId)
		breadcrumbs = [{"url" : url_for("tags.selectTag", selectedClass = "Root"), "text" : ".."},
			{"url" : url_for("elements.selectElement", selectedClass = "Enterprise",
				selectedId = elementAttribute.Element.ElementTemplate.Site.Enterprise.EnterpriseId),
				"text" : elementAttribute.Element.ElementTemplate.Site.Enterprise.Name},
			{"url" : url_for("elements.selectElement", selectedClass = "Site",
				selectedId = elementAttribute.Element.ElementTemplate.Site.SiteId), "text" : elementAttribute.Element.ElementTemplate.Site.Name},
			{"url" : url_for("elements.selectElement", selectedClass = "ElementTemplate",
				selectedId = elementAttribute.Element.ElementTemplate.ElementTemplateId), "text" : elementAttribute.Element.ElementTemplate.Name},
			{"url" : url_for("elements.dashboard", elementId = elementAttribute.Element.ElementId), "text" : elementAttribute.Element.Name},
			{"url" : url_for("tagValueNotes.listTagValueNotes", tagValueId = tagValue.TagValueId, elementAttributeId = elementAttribute.ElementAttributeId),
				"text" : "{}&nbsp;&nbsp;/&nbsp;&nbsp;{}".format(elementAttribute.ElementAttributeTemplate.Name, tagValue.Timestamp)}]
	elif eventFrameId:
		eventFrame = EventFrame.query.get_or_404(eventFrameId)
		eventFrameAttribute = EventFrameAttribute.query.get_or_404(eventFrameAttributeId)
		breadcrumbs = [{"url" : url_for("tags.selectTag", selectedClass = "Root"), "text" : ".."},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Enterprise",
				selectedId = eventFrame.Element.ElementTemplate.Site.Enterprise.EnterpriseId),
				"text" : eventFrame.Element.ElementTemplate.Site.Enterprise.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Site", selectedId = eventFrame.Element.ElementTemplate.Site.SiteId),
				"text" : eventFrame.Element.ElementTemplate.Site.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "ElementTemplate",
				selectedId = eventFrame.Element.ElementTemplate.ElementTemplateId), "text" : eventFrame.Element.ElementTemplate.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "EventFrameTemplate",
				selectedId = eventFrame.EventFrameTemplate.EventFrameTemplateId), "text" : eventFrame.EventFrameTemplate.Name},
			{"url" : url_for("eventFrames.dashboard", eventFrameId = eventFrame.EventFrameId), "text" : eventFrame.friendlyName(True)},
			{"url" : url_for("tagValueNotes.listTagValueNotes", tagValueId = tagValue.TagValueId, eventFrameId = eventFrame.EventFrameId,
				eventFrameAttributeId = eventFrameAttributeId),
				"text" : "{}&nbsp;&nbsp;/&nbsp;&nbsp;{}".format(eventFrameAttribute.EventFrameAttributeTemplate.Name, tagValue.Timestamp)}]
	else:
		breadcrumbs = [{"url" : url_for("tags.selectTag", selectedClass = "Root"), "text" : ".."},
			{"url" : url_for("tags.selectTag", selectedClass = "Enterprise", 
				selectedId = tagValue.Tag.Area.Site.Enterprise.EnterpriseId), "text" : tagValue.Tag.Area.Site.Enterprise.Name},
			{"url" : url_for("tags.selectTag", selectedClass = "Site", selectedId = tagValue.Tag.Area.Site.SiteId), "text" : tagValue.Tag.Area.Site.Name},
			{"url" : url_for("tags.selectTag", selectedClass = "Area", selectedId = tagValue.Tag.Area.AreaId), "text" : tagValue.Tag.Area.Name},
			{"url" : url_for("tagValues.listTagValues", tagId = tagValue.Tag.TagId), "text" : tagValue.Tag.Name},
			{"url" : url_for("tagValueNotes.listTagValueNotes", tagValueId = tagValue.TagValueId), "text" : tagValue.Timestamp}]

	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@tagValueNotes.route("/tagValueNotes/delete/<int:noteId>/<int:tagValueId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def deleteTagValueNote(noteId, tagValueId):
	tagValueNote = TagValueNote.query.filter_by(TagValueId = tagValueId, NoteId = noteId).first()
	note = Note.query.get_or_404(noteId)
	db.session.delete(tagValueNote)
	db.session.delete(note)
	db.session.commit()
	flash("You have successfully deleted the tag value note.", "alert alert-success")
	return redirect(request.referrer)

@tagValueNotes.route("/tagValueNotes/edit/<int:noteId>/<int:tagValueId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def editTagValueNote(noteId, tagValueId):
	operation = "Edit"
	modelName = "Tag Value Note"
	note = Note.query.get_or_404(noteId)
	form = TagValueNoteForm()

	# Edit an existing tag value note.
	if form.validate_on_submit():
		note.Note = form.note.data
		note.Timestamp = form.timestamp.data
		db.session.commit()
		flash("You have successfully edited the Tag Value Note.", "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to edit an existing tag value.
	form.note.data = note.Note
	form.timestamp.data = note.Timestamp
	form.requestReferrer.data = request.referrer
	tagValue = TagValue.query.get_or_404(tagValueId)
	breadcrumbs = [{"url" : url_for("tags.selectTag", selectedClass = "Root"), "text" : ".."},
		{"url" : url_for("tags.selectTag", selectedClass = "Enterprise",
			selectedId = tagValue.Tag.Area.Site.Enterprise.EnterpriseId), "text" : tagValue.Tag.Area.Site.Enterprise.Name},
		{"url" : url_for("tags.selectTag", selectedClass = "Site", selectedId = tagValue.Tag.Area.Site.SiteId),
			"text" : tagValue.Tag.Area.Site.Name},
		{"url" : url_for("tags.selectTag", selectedClass = "Area", selectedId = tagValue.Tag.Area.AreaId),
			"text" : tagValue.Tag.Area.Name},
		{"url" : url_for("tagValues.listTagValues", tagId = tagValue.Tag.TagId), "text" : tagValue.Tag.Name},
		{"url" : url_for("tagValueNotes.listTagValueNotes", tagValueId = tagValue.TagValueId), "text" : tagValue.Timestamp}]
	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)
