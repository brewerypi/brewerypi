from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import and_
from . import elements
from . forms import ElementForm
from .. import db
from .. decorators import adminRequired, permissionRequired
from .. models import Area, Element, ElementAttribute, ElementAttributeTemplate, ElementTemplate, Enterprise, EventFrame, EventFrameAttribute, \
	EventFrameAttributeTemplate, EventFrameTemplate, Permission, Site, Tag

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
		if form.isManaged.data:
			# Add element attributes
			for elementAttributeTemplate in ElementAttributeTemplate.query.filter_by(ElementTemplateId = element.ElementTemplateId):
				tagName = "{}_{}".format(form.name.data, elementAttributeTemplate.Name.replace(" ", ""))
				tag = Tag(AreaId = form.area.data, LookupId = elementAttributeTemplate.LookupId, Name = tagName, 
					UnitOfMeasurementId = elementAttributeTemplate.UnitOfMeasurementId)

				if tag.exists():
					tag = Tag.query.filter_by(AreaId = tag.AreaId, Name = tag.Name).one()
				else:
					db.session.add(tag)
					db.session.commit()

				elementAttribute = ElementAttribute(ElementAttributeTemplateId = elementAttributeTemplate.ElementAttributeTemplateId, 
					ElementId = element.ElementId, TagId = tag.TagId)
				db.session.add(elementAttribute)
				db.session.commit()

			# Add event frame attributes
			for topLevelEventFrameTemplate in EventFrameTemplate.query.filter_by(ElementTemplateId = element.ElementTemplateId):
				for eventFrameTemplate in topLevelEventFrameTemplate.lineage([], 0):
					for eventFrameAttributeTemplate in eventFrameTemplate["eventFrameTemplate"].EventFrameAttributeTemplates:
						tagName = "{}_{}".format(form.name.data, eventFrameAttributeTemplate.Name.replace(" ", ""))
						tag = Tag(AreaId = form.area.data, LookupId = eventFrameAttributeTemplate.LookupId, Name = tagName, 
							UnitOfMeasurementId = eventFrameAttributeTemplate.UnitOfMeasurementId)

						if tag.exists():
							tag = Tag.query.filter_by(AreaId = tag.AreaId, Name = tag.Name).one()
						else:
							db.session.add(tag)
							db.session.commit()

						eventFrameAttribute = EventFrameAttribute(EventFrameAttributeTemplateId = eventFrameAttributeTemplate.EventFrameAttributeTemplateId, 
							ElementId = element.ElementId, TagId = tag.TagId)
						db.session.add(eventFrameAttribute)
						db.session.commit()

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
	del form.isManaged
	del form.area

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
	tags = []
	if element.isManaged():
		for elementAttribute in element.ElementAttributes:
			tags.append(elementAttribute.Tag)
		for eventFrameAttribute in element.EventFrameAttributes:
			tags.append(eventFrameAttribute.Tag)

	element.delete()
	db.session.commit()
	flash('You have successfully deleted the element "{}".'.format(element.Name), "alert alert-success")
	deletedTagsMessage = ""
	tags.sort(key = lambda tag: tag.Name)
	for tag in tags:
		if not tag.isReferenced():
			tag.delete()
			if deletedTagsMessage == "":
				deletedTagsMessage = 'Deleted the following tag(s):<br>"{}"'.format(tag.Name)
			else:
				deletedTagsMessage = '{}<br>"{}"'.format(deletedTagsMessage, tag.Name)

	db.session.commit()
	if deletedTagsMessage != "":
		alert = "alert alert-success"
		flash(deletedTagsMessage, alert)

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
		oldElementName = element.Name
		element.Description = form.description.data
		element.ElementTemplateId = form.elementTemplateId.data
		element.Name = form.name.data
		element.TagAreaId = form.area.data if form.isManaged.data else None

		if form.isManaged.data:
			# Update/Add tags and element attributes
			for elementAttributeTemplate in ElementAttributeTemplate.query.filter_by(ElementTemplateId = element.ElementTemplateId):
				elementAttribute = ElementAttribute.query.filter_by(ElementAttributeTemplateId = elementAttributeTemplate.ElementAttributeTemplateId, 
					ElementId = elementId).one_or_none()

				tagUpdated = False
				tagName = "{}_{}".format(form.name.data, elementAttributeTemplate.Name.replace(" ", ""))
				newTag = Tag.query.filter_by(AreaId = form.area.data, Name = tagName).one_or_none()
				
				# Update existing bound tag or delete existing element attribute
				if elementAttribute is not None:
					oldTag = Tag.query.filter_by(TagId = elementAttribute.TagId).one()
					if newTag is None and oldTag.Name.split("_")[1] == elementAttributeTemplate.Name.replace(" ", ""):
						oldTag.AreaId = form.area.data
						oldTag.LookupId = elementAttributeTemplate.LookupId
						oldTag.Name = tagName
						oldTag.UnitOfMeasurementId = elementAttributeTemplate.UnitOfMeasurementId
						tagUpdated = True
					else:
						elementAttribute.delete()

				# Update/Add tag and add element attribute
				if not tagUpdated:
					oldTagName = "{}_{}".format(oldElementName, elementAttributeTemplate.Name.replace(" ", ""))
					oldTag = Tag.query.filter_by(AreaId = form.area.data, Name = oldTagName).one_or_none()
				
					# If new tag already exists, bind to element attribute
					if newTag is not None:
						newTag.LookupId = elementAttributeTemplate.LookupId
						newTag.UnitOfMeasurementId = elementAttributeTemplate.UnitOfMeasurementId

						elementAttribute = ElementAttribute(ElementAttributeTemplateId = elementAttributeTemplate.ElementAttributeTemplateId, 
							ElementId = elementId, TagId = newTag.TagId)
						db.session.add(elementAttribute)
					# If old tag exists but not bound, update it and bind to element attribute
					elif oldTag is not None:
						oldTag.AreaId = form.area.data
						oldTag.LookupId = elementAttributeTemplate.LookupId
						oldTag.Name = tagName
						oldTag.UnitOfMeasurementId = elementAttributeTemplate.UnitOfMeasurementId

						elementAttribute = ElementAttribute(ElementAttributeTemplateId = elementAttributeTemplate.ElementAttributeTemplateId, 
							ElementId = elementId, TagId = oldTag.TagId)
						db.session.add(elementAttribute)
					# Else add new tag and element attribute
					else:
						newTag = Tag(AreaId = form.area.data, LookupId = elementAttributeTemplate.LookupId, Name = tagName, 
							UnitOfMeasurementId = elementAttributeTemplate.UnitOfMeasurementId)
						db.session.add(newTag)
						db.session.commit()

						elementAttribute = ElementAttribute(ElementAttributeTemplateId = elementAttributeTemplate.ElementAttributeTemplateId, 
							ElementId = elementId, TagId = newTag.TagId)
						db.session.add(elementAttribute)

			# Update/Add tags and event frame attributes
			for topLevelEventFrameTemplate in EventFrameTemplate.query.filter_by(ElementTemplateId = element.ElementTemplateId):
				for eventFrameTemplate in topLevelEventFrameTemplate.lineage([], 0):
					for eventFrameAttributeTemplate in eventFrameTemplate["eventFrameTemplate"].EventFrameAttributeTemplates:
						eventFrameAttribute = EventFrameAttribute.query. \
							filter_by(EventFrameAttributeTemplateId = eventFrameAttributeTemplate.EventFrameAttributeTemplateId, ElementId = elementId). \
							one_or_none()
						
						tagUpdated = False
						tagName = "{}_{}".format(form.name.data, eventFrameAttributeTemplate.Name.replace(" ", ""))
						newTag = Tag.query.filter_by(AreaId = form.area.data, Name = tagName).one_or_none()

						# Update existing bound tag or delete existing event frame attribute
						if eventFrameAttribute is not None:
							oldTag = Tag.query.filter_by(TagId = eventFrameAttribute.TagId).one()
							if oldTag.Name.split("_")[1] == eventFrameAttributeTemplate.Name.replace(" ", ""):
								oldTag.AreaId = form.area.data
								oldTag.LookupId = eventFrameAttributeTemplate.LookupId
								oldTag.Name = tagName
								oldTag.UnitOfMeasurementId = eventFrameAttributeTemplate.UnitOfMeasurementId
								tagUpdated = True
							else:
								eventFrameAttribute.delete()

						# Update/Add tag and add event frame attribute
						if not tagUpdated:
							oldTagName = "{}_{}".format(oldElementName, eventFrameAttributeTemplate.Name.replace(" ", ""))
							oldTag = Tag.query.filter_by(AreaId = form.area.data, Name = oldTagName).one_or_none()
						
							# If new tag already exists, bind to event frame attribute
							if newTag is not None:
								newTag.LookupId = eventFrameAttributeTemplate.LookupId
								newTag.UnitOfMeasurementId = eventFrameAttributeTemplate.UnitOfMeasurementId

								eventFrameAttribute = EventFrameAttribute(EventFrameAttributeTemplateId = eventFrameAttributeTemplate.EventFrameAttributeTemplateId, ElementId = elementId, TagId = newTag.TagId)
								db.session.add(eventFrameAttribute)
							# If old tag exists but not bound, update it and bind to event frame attribute
							elif oldTag is not None:
								oldTag.AreaId = form.area.data
								oldTag.LookupId = eventFrameAttributeTemplate.LookupId
								oldTag.Name = tagName
								oldTag.UnitOfMeasurementId = eventFrameAttributeTemplate.UnitOfMeasurementId

								eventFrameAttribute = EventFrameAttribute(EventFrameAttributeTemplateId = eventFrameAttributeTemplate.EventFrameAttributeTemplateId, ElementId = elementId, TagId = oldTag.TagId)
								db.session.add(eventFrameAttribute)
							# Else add new tag and event frame attribute
							else:
								newTag = Tag(AreaId = form.area.data, LookupId = eventFrameAttributeTemplate.LookupId, Name = tagName, 
									UnitOfMeasurementId = eventFrameAttributeTemplate.UnitOfMeasurementId)
								db.session.add(newTag)
								db.session.commit()

								eventFrameAttribute = EventFrameAttribute(EventFrameAttributeTemplateId = eventFrameAttributeTemplate.EventFrameAttributeTemplateId, ElementId = elementId, TagId = newTag.TagId)
								db.session.add(eventFrameAttribute)

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
		parent = Site.query.join(Enterprise).order_by(Enterprise.Name, Site.Name).first()
		if parent is None:
			flash("You must create a Site first.", "alert alert-danger")
			return redirect(request.referrer)
		else:
			children = ElementTemplate.query.filter_by(SiteId = parent.id())
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
