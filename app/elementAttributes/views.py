from flask import flash, redirect, render_template, url_for

from . import elementAttributes

from . forms import ElementAttributeValueForm

from .. import db

from .. models import AttributeTemplate, Element, ElementAttribute, LookupValue, Tag, TagValue

from .. tagValues . forms import TagValueForm

@elementAttributes.route("/elementAttributeValues/<int:elementId>", methods = ["GET", "POST"])
# @login_required
def listElementAttributeValues(elementId):
	# check_admin()

	elementAttributes = ElementAttribute.query. \
		join(AttributeTemplate). \
		filter(ElementAttribute.ElementId == elementId). \
		order_by(AttributeTemplate.Name)		

	return render_template("elementAttributes/elementAttributeValuesDashboard.html", elementAttributes = elementAttributes)

@elementAttributes.route("/elementAttributes/addValue/<int:elementId>/<int:tagId>", methods = ["GET", "POST"])
# @login_required
def addElementAttributeValue(elementId, tagId):
	# check_admin()

	operation = "Add"
	tag = Tag.query.get_or_404(tagId)
	form = TagValueForm()

	# Configure the form based on if the element attribute value is associated with a lookup.
	if tag.LookupId:
		form.lookupValue.choices = [(lookupValue.Value, lookupValue.Name) for lookupValue in LookupValue.query.filter_by(LookupId = tag.LookupId)]
		del form.value
	else:
		del form.lookupValue

	# Add a new element attribute value.
	if form.validate_on_submit():
		if tag.LookupId:
			tagValue = TagValue(TagId = form.tagId.data, Timestamp = form.timestamp.data, Value = form.lookupValue.data)
		else:
			tagValue = TagValue(TagId = form.tagId.data, Timestamp = form.timestamp.data, Value = form.value.data)

		db.session.add(tagValue)
		db.session.commit()
		flash("You have successfully added a new element attribute value.")

		return redirect(url_for("elementAttributes.listElementAttributeValues", elementId = elementId))

	# Present a form to add a new element attribute value.
	form.tagId.data = tag.TagId
	return render_template("elementAttributes/elementAttributeValue.html", form = form, operation = operation)

@elementAttributes.route("/elementAttributes/deleteValue/<int:elementId>/<int:tagValueId>", methods = ["GET", "POST"])
# @login_required
def deleteElementAttributeValue(elementId, tagValueId):
	# check_admin()

	tagValue = TagValue.query.get_or_404(tagValueId)
	db.session.delete(tagValue)
	db.session.commit()
	flash("You have successfully deleted the element attribute value.")

	return redirect(url_for("elementAttributes.listElementAttributeValues", elementId = elementId))

@elementAttributes.route("/elementAttributes/editValue/<int:elementId>/<int:tagValueId>", methods = ["GET", "POST"])
# @login_required
def editElementAttributeValue(elementId, tagValueId):
	# check_admin()

	operation = "Edit"
	tagValue = TagValue.query.get_or_404(tagValueId)
	tag = Tag.query.get_or_404(tagValue.TagId)
	form = ElementAttributeValueForm(obj = tagValue)

	# Configure the form based on if the element attribute value is associated with a lookup.
	if tag.LookupId:
		form.lookupValue.choices = [(lookupValue.Value, lookupValue.Name) for lookupValue in LookupValue.query.filter_by(LookupId = tag.LookupId)]
		del form.value
	else:
		del form.lookupValue

	# Edit an existing element attribute value.
	if form.validate_on_submit():
		tagValue.TagId = form.tagId.data
		tagValue.Timestamp = form.timestamp.data

		if tag.LookupId:
			tagValue.Value = form.lookupValue.data
		else:
			tagValue.Value = form.value.data

		db.session.commit()

		flash("You have successfully edited the element attribute value.")

		return redirect(url_for("elementAttributes.listElementAttributeValues", elementId = elementId))

	# Present a form to edit an existing element attribute value.
	form.tagId.data = tagValue.TagId
	form.timestamp.data = tagValue.Timestamp

	if tag.LookupId:
		form.lookupValue.data = tagValue.Value
	else:
		form.value.data = tagValue.Value

	return render_template("elementAttributes/elementAttributeValue.html", form = form, operation = operation)
