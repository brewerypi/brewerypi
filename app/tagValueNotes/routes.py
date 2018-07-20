from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import or_
from . import tagValueNotes
from . forms import TagValueNoteForm
from .. import db
from .. decorators import permissionRequired
from .. models import ElementAttribute, Note, Permission, TagValue, TagValueNote

modelName = "Tag Value Note"

@tagValueNotes.route("/tagValueNotes/<int:tagValueId>", methods = ["GET", "POST"])
@tagValueNotes.route("/tagValueNotes/<int:tagValueId>/<int:elementAttributeId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def listTagValueNotes(tagValueId, elementAttributeId = None):
	if elementAttributeId:
		elementAttribute = ElementAttribute.query.get_or_404(elementAttributeId)
	else:
		elementAttribute = None

	tagValue = TagValue.query.get_or_404(tagValueId)
	tagValueNotes = TagValueNote.query.filter_by(TagValueId = tagValueId)
	return render_template("tagValueNotes/tagValueNotes.html", elementAttribute = elementAttribute, tagValue = tagValue, tagValueNotes = tagValueNotes)

@tagValueNotes.route("/tagValueNotes/add/<int:tagValueId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def addTagValueNote(tagValueId):
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
	breadcrumbs = [{"url" : url_for("tags.selectTag", selectedClass = "Root"), "text" : ".."},
		{"url" : url_for("tags.selectTag", selectedClass = "Enterprise", 
			selectedId = tagValue.Tag.Area.Site.Enterprise.EnterpriseId), "text" : tagValue.Tag.Area.Site.Enterprise.Name},
		{"url" : url_for("tags.selectTag", selectedClass = "Site", selectedId = tagValue.Tag.Area.Site.SiteId), "text" : tagValue.Tag.Area.Site.Name},
		{"url" : url_for("tags.selectTag", selectedClass = "Area", selectedId = tagValue.Tag.Area.AreaId), "text" : tagValue.Tag.Area.Name},
		{"url" : url_for("tagValues.listTagValues", tagId = tagValue.Tag.TagId), "text" : tagValue.Tag.Name},
		{"url" : url_for("tagValueNotes.listTagValueNotes", tagValueId = tagValue.TagValueId), "text" : tagValue.Timestamp}]
	return render_template("addEditModel.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

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
	return render_template("addEditModel.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)
