from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import or_
from . import tagValues
from . forms import TagValueForm, TagValueNoteForm
from .. import db
from .. decorators import permissionRequired
from .. models import Area, ElementAttribute, Enterprise, Lookup, LookupValue, Note, Permission, Site, Tag, TagValue, TagValueNote

modelName = "Tag Value"

@tagValues.route("/tagValues/<int:tagId>", methods = ["GET", "POST"])
@tagValues.route("/tagValues/<int:tagId>/<int:elementAttributeId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def listTagValues(tagId, elementAttributeId = None, ):
	if elementAttributeId:
		elementAttribute = ElementAttribute.query.get_or_404(elementAttributeId)
	else:
		elementAttribute = None

	tag = Tag.query.get_or_404(tagId)
	if tag.LookupId:
		tagValues = TagValue.query.join(Tag, Lookup, LookupValue).filter(Tag.TagId == tagId, TagValue.Value == LookupValue.Value)
	else:
		tagValues = TagValue.query.filter_by(TagId = tagId)
	return render_template("tagValues/tagValues.html", elementAttribute = elementAttribute, tag = tag, tagValues = tagValues)

@tagValues.route("/tagValues/add/<int:tagId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def addTagValue(tagId):
	operation = "Add"
	tag = Tag.query.get_or_404(tagId)
	form = TagValueForm()

	# Configure the form based on if the tag value is associated with a lookup.
	if tag.LookupId:
		form.lookupValue.choices = [(lookupValue.Value, lookupValue.Name) for lookupValue in LookupValue.query. \
			filter(LookupValue.LookupId == tag.LookupId, LookupValue.Selectable == True)]
		del form.value
	else:
		del form.lookupValue

	# Add a new tag value.
	if form.validate_on_submit():
		if tag.LookupId:
			tagValue = TagValue(TagId = form.tagId.data, Timestamp = form.timestamp.data, Value = form.lookupValue.data)
		else:
			tagValue = TagValue(TagId = form.tagId.data, Timestamp = form.timestamp.data, Value = form.value.data)

		db.session.add(tagValue)
		db.session.commit()
		flash("You have successfully added a new tag value.", "alert alert-success")
		return redirect(url_for("tagValues.listTagValues", tagId = tag.TagId))

	# Present a form to add a new tag value.
	form.tagId.data = tagId
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@tagValues.route("/tagValues/delete/<int:tagValueId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def deleteTagValue(tagValueId):
	tagValue = TagValue.query.get_or_404(tagValueId)
	db.session.delete(tagValue)
	db.session.commit()
	flash("You have successfully deleted the tag value.", "alert alert-success")
	return redirect(url_for("tagValues.listTagValues", tagId = tagValue.TagId))

@tagValues.route("/tagValues/edit/<int:tagValueId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def editTagValue(tagValueId):
	operation = "Edit"
	tagValue = TagValue.query.get_or_404(tagValueId)
	tag = Tag.query.get_or_404(tagValue.TagId)
	form = TagValueForm(obj = tagValue)

	# Configure the form based on if the tag value is associated with a lookup.
	if tag.LookupId:
		form.lookupValue.choices = [(lookupValue.Value, lookupValue.Name) for lookupValue in LookupValue.query. \
			filter(LookupValue.LookupId == tag.LookupId, or_(LookupValue.Selectable == True, LookupValue.Value == tagValue.Value))]
		del form.value
	else:
		del form.lookupValue

	# Edit an existing tagValue.
	if form.validate_on_submit():
		tagValue.TagId = form.tagId.data
		tagValue.Timestamp = form.timestamp.data

		if tag.LookupId:
			tagValue.Value = form.lookupValue.data
		else:
			tagValue.Value = form.value.data

		db.session.commit()
		flash("You have successfully edited the tag value.", "alert alert-success")
		return redirect(url_for("tagValues.listTagValues", tagId = tagValue.TagId))

	# Present a form to edit an existing tagValue.
	form.tagId.data = tagValue.TagId
	form.timestamp.data = tagValue.Timestamp

	if tag.LookupId:
		form.lookupValue.data = tagValue.Value
	else:
		form.value.data = tagValue.Value

	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@tagValues.route("/tagValues/addTagValueNote/<int:tagValueId>", methods = ["GET", "POST"])
# @login_required
def addTagValueNote(tagValueId):
	# check_admin()
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
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@tagValues.route("/tagValues/editTagValueNote/<int:noteId>", methods = ["GET", "POST"])
# @login_required
def editTagValueNote(noteId):
	# check_admin()
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
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@tagValues.route("/tagValues/deleteTagValueNote/<int:tagValueId>/<int:noteId>", methods = ["GET", "POST"])
# @login_required
def deleteTagValueNote(tagValueId, noteId):
	# check_admin()
	tagValueNote = TagValueNote.query.filter_by(TagValueId = tagValueId, NoteId = noteId).first()
	note = Note.query.get_or_404(noteId)
	db.session.delete(tagValueNote)
	db.session.delete(note)
	db.session.commit()
	flash("You have successfully deleted the tag value note.", "alert alert-success")
	return redirect(request.referrer)
