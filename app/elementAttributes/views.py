from flask import flash, redirect, render_template, url_for
from sqlalchemy import or_
from . import elementAttributes
from . forms import ElementAttributeForm, ElementAttributeValueForm
from .. import db
from .. models import AttributeTemplate, Element, ElementAttribute, ElementTemplate, Enterprise, LookupValue, Site, Tag, TagValue
from .. tagValues . forms import TagValueForm

@elementAttributes.route("/elementAttributes", methods = ["GET", "POST"])
# @login_required
def listElementAttributes():
	# check_admin()
	elementAttributes = ElementAttribute.query.join(Element, Tag, ElementTemplate, Site, Enterprise). \
		join(AttributeTemplate, ElementAttribute.AttributeTemplateId == AttributeTemplate.AttributeTemplateId). \
		order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, Element.Name, AttributeTemplate.Name)
	return render_template("elementAttributes/elementAttributes.html", elementAttributes = elementAttributes)

@elementAttributes.route("/elementAttributes/add", methods = ["GET", "POST"])
# @login_required
def addElementAttribute():
	# check_admin()
	modelName = "Element Attribute"
	operation = "Add"
	form = ElementAttributeForm()

	# Add a new element attribute.
	if form.validate_on_submit():
		elementAttribute = ElementAttribute(AttributeTemplate = form.attributeTemplate.data, Element = form.element.data, Tag = form.tag.data)
		db.session.add(elementAttribute)
		db.session.commit()
		flash("You have successfully added the element attribute \"" + form.attributeTemplate.data.Name + "\" for \"" + form.element.data.Name + "\".")
		return redirect(url_for("elementAttributes.listElementAttributes"))

	# Present a form to add a new element attribute.
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@elementAttributes.route("/elementAttributes/delete/<int:elementAttributeId>", methods = ["GET", "POST"])
# @login_required
def deleteElementAttribute(elementAttributeId):
	# check_admin()
	elementAttribute = ElementAttribute.query.get_or_404(elementAttributeId)
	attributeTemplateName = elementAttribute.AttributeTemplate.Name
	elementName = elementAttribute.Element.Name
	db.session.delete(elementAttribute)
	db.session.commit()
	flash("You have successfully deleted the element attribute \"" + attributeTemplateName + "\" for \"" + elementName + "\".")
	return redirect(url_for("elementAttributes.listElementAttributes"))

@elementAttributes.route("/elementAttributes/edit/<int:elementAttributeId>", methods = ["GET", "POST"])
# @login_required
def editElementAttribute(elementAttributeId):
	# check_admin()
	modelName = "Element Attribute"
	operation = "Add"
	elementAttribute = ElementAttribute.query.get_or_404(elementAttributeId)
	form = ElementAttributeForm(obj = elementAttribute)

	# Edit an existing element attribute.
	if form.validate_on_submit():	
		elementAttribute.AttributeTemplate = form.attributeTemplate.data
		elementAttribute.Element = form.element.data
		elementAttribute.Tag = form.tag.data
		db.session.commit()
		flash("You have successfully edited the element attribute \"" + elementAttribute.AttributeTemplate.Name + "\" for \"" + \
			elementAttribute.Element.Name + "\".")
		return redirect(url_for("elementAttributes.listElementAttributes"))

	# Present a form to edit an existing element attribute.
	form.attributeTemplate.data = elementAttribute.AttributeTemplate
	form.element.data = elementAttribute.Element
	form.tag.data = elementAttribute.Tag
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

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
	modelName = "Element Attribute Value"
	operation = "Add"
	tag = Tag.query.get_or_404(tagId)
	form = TagValueForm()

	# Configure the form based on if the element attribute value is associated with a lookup.
	if tag.LookupId:
		form.lookupValue.choices = [(lookupValue.Value, lookupValue.Name) for lookupValue in LookupValue.query. \
			filter(LookupValue.LookupId == tag.LookupId, LookupValue.Selectable == True)]
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
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

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
	modelName = "Element Attribute Value"
	operation = "Edit"
	tagValue = TagValue.query.get_or_404(tagValueId)
	tag = Tag.query.get_or_404(tagValue.TagId)
	form = ElementAttributeValueForm(obj = tagValue)

	# Configure the form based on if the element attribute value is associated with a lookup.
	if tag.LookupId:
		form.lookupValue.choices = [(lookupValue.Value, lookupValue.Name) for lookupValue in LookupValue.query. \
			filter(LookupValue.LookupId == tag.LookupId, or_(LookupValue.Selectable == True, LookupValue.Value == tagValue.Value))]
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

	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)
