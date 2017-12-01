from flask import flash, redirect, render_template, url_for

from . import dataEntry

from . forms import ElementForm, ElementAttributeValueForm

from .. import db

from .. models import AttributeTemplate, Element, ElementAttribute, \
	ElementTemplate, Enterprise, Site, Tag, TagValue

@dataEntry.route('/elementAttributes/<int:id>', methods=['GET', 'POST'])
# @login_required
def list_elementAttributes(id):
	# check_admin()

	element = Element.query.get_or_404(id)

	elementAttributes = ElementAttribute.query. \
		join(AttributeTemplate, Tag). \
		outerjoin(TagValue). \
		filter(ElementAttribute.ElementId == element.ElementId). \
		order_by(AttributeTemplate.Name)		

	return render_template('dataEntry/elementAttributes.html', elementAttributes=elementAttributes, elementName=element.Name)

@dataEntry.route('/elementAttributes/add/<int:elementId>/<int:tagId>', methods=['GET', 'POST'])
# @login_required
def add_elementAttributeValue(elementId, tagId):
	# check_admin()

	attributeTemplate = AttributeTemplate.query.join(ElementAttribute). \
		filter(ElementAttribute.ElementId == elementId, ElementAttribute.TagId == tagId)

	element = Element.query.filter_by(ElementId = elementId)

	tag = Tag.query.get_or_404(tagId)
	form = ElementAttributeValueForm()

	# Add a new element attribute value.
	if form.validate_on_submit():

		tagValue = TagValue(Tag=tag, Timestamp=form.timestamp.data, Value=form.value.data)
		db.session.add(tagValue)
		db.session.commit()
		flash("You have successfully added a new " + attributeTemplate[0].Name + " entry for " + element[0].Name + ".")

		return redirect(url_for('dataEntry.list_elementAttributes', id=elementId))

	# Present a form to add a new element attribute value.
	return render_template('dataEntry/elementAttributeValue.html', attributeTemplate=attributeTemplate, element=element, form=form)

@dataEntry.route('/elementAttributes/delete/<int:elementId>/<int:tagValueId>', methods=['GET', 'POST'])
# @login_required
def delete_elementAttributeValue(elementId, tagValueId):
	# check_admin()

	attributeTemplates = AttributeTemplate.query.join(ElementAttribute, Element, Tag, TagValue). \
		filter(ElementAttribute.ElementId == elementId, TagValue.TagValueId == tagValueId)	

	attributeTemplate = attributeTemplates[0].Name
	element = attributeTemplates[0].ElementAttributes[0].Element.Name

	tagValue = TagValue.query.get_or_404(tagValueId)
	db.session.delete(tagValue)
	db.session.commit()
	flash("You have successfully deleted a " + attributeTemplate + " entry for " + element + ".")

	return redirect(url_for('dataEntry.list_elementAttributes', id=elementId))

@dataEntry.route('/elementAttributes/edit/<int:elementId>/<int:tagValueId>', methods=['GET', 'POST'])
# @login_required
def edit_elementAttributeValue(elementId, tagValueId):
	# check_admin()

	attributeTemplate = AttributeTemplate.query.join(ElementAttribute, Tag, TagValue). \
		filter(ElementAttribute.ElementId == elementId, TagValue.TagValueId == tagValueId)

	element = Element.query.filter_by(ElementId = elementId)

	tagValue = TagValue.query.get_or_404(tagValueId)
	form = ElementAttributeValueForm(obj=tagValue)

	# Edit an existing element attribute value.
	if form.validate_on_submit():
		tagValue.Timestamp = form.timestamp.data
		tagValue.Value = form.value.data

		db.session.commit()

		flash("You have successfully edited the " + attributeTemplate[0].Name + " for " + element[0].Name + ".")

		return redirect(url_for('dataEntry.list_elementAttributes', id=elementId))

	# Present a form to edit an existing element attribute value.
	form.timestamp.data = tagValue.Timestamp
	form.value.data = tagValue.Value
	return render_template('dataEntry/elementAttributeValue.html', attributeTemplate=attributeTemplate, element=element, form=form)

@dataEntry.route('/elements', methods=['GET', 'POST'])
# @login_required
def list_elements():
	# check_admin()

	form = ElementForm()

	if form.validate_on_submit():

		element = form.element.data

		return redirect(url_for('dataEntry.list_elementAttributes', id=element.ElementId))

	# Present a form to select an element.
	elements = Element.query.join(ElementTemplate, Site, Enterprise).order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, Element.Name)
	return render_template('dataEntry/elements.html', elements=elements, form=form)
