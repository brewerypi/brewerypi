from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import and_
from . import elements
from . forms import ElementForm
from .. import db
from .. decorators import adminRequired, permissionRequired
from .. models import Area, ElementAttributeTemplate, Element, ElementAttribute, ElementTemplate, Enterprise, EventFrame, EventFrameTemplate, Permission, Site, Tag

modelName = "Element"

@elements.route("/elements/add/<int:elementTemplateId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def addElement(elementTemplateId):
	operation = "Add"
	form = ElementForm()
	elementTemplate = ElementTemplate.query.get_or_404(elementTemplateId)
	form.area.choices = [(area.AreaId, area.Name) for area in Area.query.filter_by(SiteId = elementTemplate.Site.SiteId).order_by(Area.Name)]

	# Add a new element.
	if form.validate_on_submit():
		element = Element(Description = form.description.data, ElementTemplateId = form.elementTemplateId.data,
			TagAreaId = form.area.data if form.isManaged.data else None, Name = form.name.data)
		db.session.add(element)
		db.session.commit()

		# Add tags and element attributes
		if form.isManaged.data:
			elementAttributeTemplates = ElementAttributeTemplate.query.filter_by(ElementTemplateId = element.ElementTemplateId).all()
			addedTags = []
			skippedTags = []
			addedElementAttributes = []

			for elementAttributeTemplate in elementAttributeTemplates:
				tagName = "{}_{}".format(form.name.data, elementAttributeTemplate.Name.replace(" ", ""))
				tag = Tag(AreaId = form.area.data, LookupId = elementAttributeTemplate.LookupId, Name = tagName, 
					UnitOfMeasurementId = elementAttributeTemplate.UnitOfMeasurementId)

				if tag.exists():
					skippedTags.append(tagName)
					tag = Tag.query.filter_by(AreaId = tag.AreaId, Name = tag.Name).one()
				else:
					addedTags.append(tagName)
					db.session.add(tag)
					db.session.commit()

				elementAttribute = ElementAttribute(ElementAttributeTemplateId = elementAttributeTemplate.ElementAttributeTemplateId, 
					ElementId = element.ElementId, TagId = tag.TagId)
				addedElementAttributes.append(elementAttributeTemplate.Name)
				db.session.add(elementAttribute)
				db.session.commit()

			if skippedTags:
				flash("The following tags already exist: {}.".format(skippedTags), "alert alert-warning")
			if addedTags:
				flash("The following tags were created: {}.".format(addedTags), "alert alert-success")
			if addedElementAttributes:
				flash("The following element attributes were bound to tags: {}.".format(addedElementAttributes), "alert alert-success")

		flash("You have successfully added the new element \"{}\".".format(element.Name), "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to add a new element.
	form.elementTemplateId.data = elementTemplateId
	if form.requestReferrer.data is None:
		form.requestReferrer.data = request.referrer

	breadcrumbs = [{"url" : url_for("elements.selectElement", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
		{"url" : url_for("elements.selectElement", selectedClass = "Enterprise", selectedId = elementTemplate.Site.Enterprise.EnterpriseId),
			"text" : elementTemplate.Site.Enterprise.Name},
		{"url" : url_for("elements.selectElement", selectedClass = "Site", selectedId = elementTemplate.Site.SiteId), "text" : elementTemplate.Site.Name},
		{"url" : url_for("elements.selectElement", selectedClass = "ElementTemplate", selectedId = elementTemplate.ElementTemplateId),
			"text" : elementTemplate.Name}]
	return render_template("elements/addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

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
			return redirect(form.requestReferrer.data)
		element = Element(Description = form.description.data, ElementTemplate = elementToCopy.ElementTemplate, Name = form.name.data)
		db.session.add(element)

		elementAttributeTemplateIds = []
		tags = []
		for elementAttribute in elementToCopy.ElementAttributes:
			elementAttributeTemplateIds.append(elementAttribute.ElementAttributeTemplateId)
			tagName = form.name.data + "_" + elementAttribute.ElementAttributeTemplate.Name.replace(" ", "")

			# Ensure the tag doesn't already exist.
			if Tag.query.join(Area).filter(Area.SiteId == elementToCopy.ElementTemplate.SiteId, Tag.Name == tagName).count() != 0:
				flash("Tag {} already exists. Add aborted.".format(tagName), "alert alert-danger")
				return redirect(form.requestReferrer.data)

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
		for elementAttributeTemplateId, tag in zip(elementAttributeTemplateIds, tags):
			elementAttribute = ElementAttribute(ElementAttributeTemplateId = elementAttributeTemplateId, ElementId = element.ElementId, TagId = tag.TagId)
			db.session.add(elementAttribute)

		db.session.commit()
		flash("You have successfully copied \"{}\" to \"{}\".".format(elementToCopy.Name, element.Name), "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to copy an element.
	del form.elementTemplateId
	form.elementIdToCopy.data = elementId
	if form.requestReferrer.data is None:
		form.requestReferrer.data = request.referrer

	element = Element.query.get_or_404(elementId)
	breadcrumbs = [{"url" : url_for("elements.selectElement", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
		{"url" : url_for("elements.selectElement", selectedClass = "Enterprise", selectedId = element.ElementTemplate.Site.Enterprise.EnterpriseId),
			"text" : element.ElementTemplate.Site.Enterprise.Name},
		{"url" : url_for("elements.selectElement", selectedClass = "Site", selectedId = element.ElementTemplate.Site.SiteId),
			"text" : element.ElementTemplate.Site.Name},
		{"url" : url_for("elements.selectElement", selectedClass = "ElementTemplate", selectedId = element.ElementTemplate.ElementTemplateId),
			"text" : element.ElementTemplate.Name},
		{"url" : None, "text" : element.Name}]
	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@elements.route("/elements/dashboard/<int:elementId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def dashboard(elementId):
	element = Element.query.get_or_404(elementId)
	elementAttributes = ElementAttribute.query.filter_by(ElementId = elementId)
	return render_template("elements/dashboard.html", elementAttributes = elementAttributes, element = element)

@elements.route("/elements/delete/<int:elementId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def deleteElement(elementId):
	element = Element.query.get_or_404(elementId)

	# Get managed tags
	tags = []
	if element.isManaged():
		for elementAttribute in element.ElementAttributes:
			tags.append(Tag.query.get_or_404(elementAttribute.TagId))
		for eventFrameAttribute in element.EventFrameAttributes:
			tags.append(Tag.query.get_or_404(eventFrameAttribute.TagId))

	element.delete()

	# Delete unreferenced tags
	for tag in tags:
		if not tag.isReferenced():
			tag.delete()

	db.session.commit()

	flash("You have successfully deleted the element \"{}\".".format(element.Name), "alert alert-success")
	return redirect(request.referrer)

@elements.route("/elements/edit/<int:elementId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def editElement(elementId):
	operation = "Edit"
	element = Element.query.get_or_404(elementId)
	form = ElementForm(obj = element)
	form.area.choices = [(area.AreaId, area.Name) for area in Area.query.filter_by(SiteId = element.ElementTemplate.Site.SiteId).order_by(Area.Name)]

	# Edit an existing element.
	if form.validate_on_submit():
		element.Description = form.description.data
		element.ElementTemplateId = form.elementTemplateId.data
		element.Name = form.name.data
		element.TagAreaId = form.area.data if form.isManaged.data else None
		db.session.commit()
		flash("You have successfully edited the element \"{}\".".format(element.Name), "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to edit an existing element.
	form.elementId.data = element.ElementId
	form.description.data = element.Description
	form.elementTemplateId.data = element.ElementTemplateId
	form.name.data = element.Name
	if element.TagAreaId is None:
		form.isManaged.data = False
	else:
		form.isManaged.data = True
		form.area.data = element.TagAreaId

	if form.requestReferrer.data is None:
		form.requestReferrer.data = request.referrer

	breadcrumbs = [{"url" : url_for("elements.selectElement", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
		{"url" : url_for("elements.selectElement", selectedClass = "Enterprise", selectedId = element.ElementTemplate.Site.Enterprise.EnterpriseId),
			"text" : element.ElementTemplate.Site.Enterprise.Name},
		{"url" : url_for("elements.selectElement", selectedClass = "Site", selectedId = element.ElementTemplate.Site.SiteId),
			"text" : element.ElementTemplate.Site.Name},
		{"url" : url_for("elements.selectElement", selectedClass = "ElementTemplate", selectedId = element.ElementTemplate.ElementTemplateId),
			"text" : element.ElementTemplate.Name},
		{"url" : None, "text" : element.Name}]
	return render_template("elements/addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@elements.route("/elements/select", methods = ["GET", "POST"]) # Default.
@elements.route("/elements/select/<string:selectedClass>", methods = ["GET", "POST"]) # Root.
@elements.route("/elements/select/<string:selectedClass>/<int:selectedId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def selectElement(selectedClass = None, selectedId = None):
	if selectedClass == None:
		parent = Site.query.join(ElementTemplate, Enterprise).order_by(Enterprise.Name).first()
		if parent:
			children = ElementTemplate.query.filter_by(SiteId = parent.id())
		else:
			parent = Site.query.join(Enterprise).order_by(Enterprise.Name).first()
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
	elif selectedClass == "ElementAttributeTemplate":
		parent = ElementTemplate.query.get_or_404(selectedId)
		children = ElementAttributeTemplate.query.filter_by(ElementTemplateId = selectedId)
		childrenClass = "ElementAttributeTemplate"

	return render_template("elements/select.html", children = children, childrenClass = childrenClass, parent = parent)
