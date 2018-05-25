from datetime import datetime
from flask import flash, redirect, render_template, url_for
from flask_login import login_required
from sqlalchemy import and_
from . import elements
from . forms import ElementForm
from .. import db
from .. eventFrames . forms import EventFrameForm
from .. decorators import adminRequired, permissionRequired
from .. models import Area, AttributeTemplate, Element, ElementAttribute, ElementTemplate, Enterprise, EventFrame, EventFrameTemplate, LookupValue, \
	Permission, Site, Tag, TagValue

modelName = "Element"

@elements.route("/elements", methods = ["GET", "POST"])
@login_required
@adminRequired
def listElements():
	elements = Element.query.all()
	return render_template("elements/elements.html", elements = elements)

@elements.route("/elements/dashboard/<int:elementId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def dashboard(elementId):
	element = Element.query.get_or_404(elementId)
	elementAttributes = ElementAttribute.query.filter_by(ElementId = elementId)
	eventFrameTemplates = EventFrameTemplate.query. \
		join(ElementTemplate, Element). \
		outerjoin(EventFrame, and_(Element.ElementId == EventFrame.ElementId, EventFrameTemplate.EventFrameTemplateId == EventFrame.EventFrameTemplateId)). \
		filter(Element.ElementId == elementId)
	return render_template("elements/elementDashboard.html", elementAttributes = elementAttributes, element = element,
		eventFrameTemplates = eventFrameTemplates)

@elements.route("/elements/add", methods = ["GET", "POST"])
@login_required
@adminRequired
def addElement():
	operation = "Add"
	form = ElementForm()

	# Add a new element.
	if form.validate_on_submit():
		element = Element(Description = form.description.data, ElementTemplate = form.elementTemplate.data, Name = form.name.data)
		db.session.add(element)
		db.session.commit()
		flash("You have successfully added the new element \"" + element.Name + "\".", "alert alert-success")
		return redirect(url_for("elements.listElements"))

	# Present a form to add a new element.
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@elements.route("/elements/copy/<int:elementId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def copyElement(elementId):
	operation = "Copy"
	form = ElementForm()

	# Copy an element.
	if form.validate_on_submit():
		elementToCopy = Element.query.get_or_404(form.elementIdToCopy.data)

		# Ensure the element doesn't already exist.
		if Element.query.filter_by(ElementTemplateId = elementToCopy.ElementTemplateId, Name = form.name.data).count() != 0:
			flash("Element " + form.name.data + " already exists. Add aborted.", "alert alert-danger")
			return redirect(url_for("elements.listElements"))
		element = Element(Description = form.description.data, ElementTemplate = elementToCopy.ElementTemplate, Name = form.name.data)
		db.session.add(element)

		attributeTemplateIds = []
		tags = []
		for elementAttribute in elementToCopy.ElementAttributes:
			attributeTemplateIds.append(elementAttribute.AttributeTemplateId)
			tagName = form.name.data + "_" + elementAttribute.AttributeTemplate.Name.replace(" ", "")

			# Ensure the tag doesn't already exist.
			if Tag.query.join(Area).filter(Area.SiteId == elementToCopy.ElementTemplate.SiteId, Tag.Name == tagName).count() != 0:
				flash("Tag " + tagName + " already exists. Add aborted.", "alert alert-danger")
				return redirect(url_for("elements.listElements"))

			if elementAttribute.Tag.Lookup:
				tag = Tag(AreaId = elementAttribute.Tag.Area.AreaId,
					Description = elementAttribute.Tag.Description.replace(elementToCopy.Name, form.name.data), LookupId = elementAttribute.Tag.LookupId,
					Name = tagName, UnitOfMeasurementId = None)
			else:
				tag = Tag(AreaId = elementAttribute.Tag.Area.AreaId,
					Description = elementAttribute.Tag.Description.replace(elementToCopy.Name, form.name.data), LookupId = None,
					Name = tagName, UnitOfMeasurementId = elementAttribute.Tag.UnitOfMeasurementId)
			
			tags.append(tag)
			db.session.add(tag)

		db.session.commit()
		for attributeTemplateId, tag in zip(attributeTemplateIds, tags):
			elementAttribute = ElementAttribute(AttributeTemplateId = attributeTemplateId, ElementId = element.ElementId, TagId = tag.TagId)
			db.session.add(elementAttribute)

		db.session.commit()
		flash("You have successfully copied \"" + elementToCopy.Name + "\" to \"" + element.Name + "\".", "alert alert-success")
		return redirect(url_for("elements.listElements"))

	# Present a form to copy an element.
	del form.elementTemplate
	form.elementIdToCopy.data = elementId
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@elements.route("/elements/delete/<int:elementId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def deleteElement(elementId):
	element = Element.query.get_or_404(elementId)
	db.session.delete(element)
	db.session.commit()
	flash("You have successfully deleted the element \"" + element.Name + "\".", "alert alert-success")
	return redirect(url_for("elements.listElements"))

@elements.route("/elements/edit/<int:elementId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def editElement(elementId):
	operation = "Edit"
	element = Element.query.get_or_404(elementId)
	form = ElementForm(obj = element)

	# Edit an existing element.
	if form.validate_on_submit():
		element.Description = form.description.data
		element.ElementTemplate = form.elementTemplate.data
		element.Name = form.name.data

		db.session.commit()
		flash("You have successfully edited the element \"" + element.Name + "\".", "alert alert-success")
		return redirect(url_for("elements.listElements"))

	# Present a form to edit an existing element.
	form.description.data = element.Description
	form.elementTemplate.data = element.ElementTemplate
	form.name.data = element.Name
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@elements.route("/selectElement", methods = ["GET", "POST"])
@elements.route("/selectElement/<string:className>", methods = ["GET", "POST"])
@elements.route("/selectElement/<string:className>/<int:id>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def selectElement(className = None, id = None):
	if className == None:
		parent = Site.query.join(Enterprise).order_by(Enterprise.Name).first()
		if parent:
			children = ElementTemplate.query.filter_by(SiteId = parent.id())
		else:
			children = None
		className = "ElementTemplate"
	elif className == "Root":
		parent = None
		children = Enterprise.query.order_by(Enterprise.Name)
		className = "Enterprise"
	elif className == "Enterprise":
		parent = Enterprise.query.get_or_404(id)
		children = Site.query.filter_by(EnterpriseId = id)
		className = "Site"
	elif className == "Site":
		parent = Site.query.get_or_404(id)
		children = ElementTemplate.query.filter_by(SiteId = id)
		className = "ElementTemplate"
	elif className == "ElementTemplate":
		parent = ElementTemplate.query.get_or_404(id)
		children = Element.query.filter_by(ElementTemplateId = id)
		className = "Element"

	return render_template("elements/selectElement.html", children = children, className = className, parent = parent)
