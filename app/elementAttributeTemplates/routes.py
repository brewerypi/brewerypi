from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from . import elementAttributeTemplates
from . forms import ElementAttributeTemplateForm
from .. import db
from .. decorators import adminRequired
from .. models import Area, ElementAttribute, ElementAttributeTemplate, ElementTemplate, Enterprise, Site, Tag

@elementAttributeTemplates.route("/elementAttributeTemplates/add/<int:elementTemplateId>", methods = ["GET", "POST"])
@elementAttributeTemplates.route("/elementAttributeTemplates/add/<int:elementTemplateId>/<int:lookup>", methods = ["GET", "POST"])
@login_required
@adminRequired
def addElementAttributeTemplate(elementTemplateId, lookup = False):
	operation = "Add"
	form = ElementAttributeTemplateForm()
	elementTemplate = ElementTemplate.query.get_or_404(elementTemplateId)

	if lookup:
		modelName = "Lookup Element Attribute Template"
		del form.unitOfMeasurement
	else:
		modelName = "Element Attribute Template"
		del form.lookup

	# Add a new elementAttributeTemplate.
	if form.validate_on_submit():
		if lookup:
			elementAttributeTemplate = ElementAttributeTemplate(Description = form.description.data, ElementTemplateId = form.elementTemplateId.data, \
				Lookup = form.lookup.data, Name = form.name.data)
		else:
			elementAttributeTemplate = ElementAttributeTemplate(Description = form.description.data, ElementTemplateId = form.elementTemplateId.data, \
				Name = form.name.data, UnitOfMeasurement = form.unitOfMeasurement.data)

		db.session.add(elementAttributeTemplate)
		db.session.commit()
		flash('You have successfully added the new element attribute template "{}".'.format(elementAttributeTemplate.Name), "alert alert-success")
		for element in elementTemplate.Elements:
			if element.isManaged():
				# Tag management.
				area = Area.query.get_or_404(element.TagAreaId)
				tagName = "{}_{}".format(element.Name, elementAttributeTemplate.Name.replace(" ", ""))
				tag = Tag.query.filter_by(AreaId = area.AreaId, Name = tagName).one_or_none()
				if tag is None:
					# Tag doesn't exist, so create it.
					tag = Tag(AreaId = area.AreaId, LookupId = elementAttributeTemplate.LookupId, Name = tagName,
						UnitOfMeasurementId = elementAttributeTemplate.UnitOfMeasurementId)
					db.session.add(tag)
				else:
					# Tag exists, so update LookupId and UnitOfMeasurementId just in case.
					tag.LookupId = elementAttributeTemplate.LookupId
					tag.UnitOfMeasurementId = elementAttributeTemplate.UnitOfMeasurementId

				db.session.commit()

				# Element attribute management.
				elementAttribute = ElementAttribute(ElementAttributeTemplateId = elementAttributeTemplate.ElementAttributeTemplateId, 
					ElementId = element.ElementId, TagId = tag.TagId)
				db.session.add(elementAttribute)
				db.session.commit()

		return redirect(form.requestReferrer.data)

	# Present a form to add a new element attribute template.
	form.elementTemplateId.data = elementTemplateId
	if form.requestReferrer.data is None:
		form.requestReferrer.data = request.referrer

	breadcrumbs = [{"url" : url_for("elements.selectElement", selectedClass = "Root"),
		"text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
		{"url" : url_for("elements.selectElement", selectedClass = "Enterprise", selectedId = elementTemplate.Site.Enterprise.EnterpriseId),
			"text" : elementTemplate.Site.Enterprise.Name},
		{"url" : url_for("elements.selectElement", selectedClass = "Site", selectedId = elementTemplate.Site.SiteId),
			"text" : elementTemplate.Site.Name},
		{"url" : url_for("elements.selectElement", selectedClass = "ElementAttributeTemplate", selectedId = elementTemplate.ElementTemplateId),
			"text" : elementTemplate.Name}]
	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@elementAttributeTemplates.route("/elementAttributeTemplates/delete/<int:elementAttributeTemplateId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def deleteElementAttributeTemplate(elementAttributeTemplateId):
	elementAttributeTemplate = ElementAttributeTemplate.query.get_or_404(elementAttributeTemplateId)
	tags = []
	for elementAttribute in elementAttributeTemplate.ElementAttributes:
		tags.append(elementAttribute.Tag)

	elementAttributeTemplate.delete()
	db.session.commit()
	flash('You have successfully deleted the element attribute template "{}".'.format(elementAttributeTemplate.Name), "alert alert-success")
	for tag in tags:
		if not tag.isReferenced():
			tag.delete()
	
	db.session.commit()
	return redirect(request.referrer)

@elementAttributeTemplates.route("/elementAttributeTemplates/edit/<int:elementAttributeTemplateId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def editElementAttributeTemplate(elementAttributeTemplateId):
	operation = "Edit"
	elementAttributeTemplate = ElementAttributeTemplate.query.get_or_404(elementAttributeTemplateId)
	form = ElementAttributeTemplateForm(obj = elementAttributeTemplate)

	if elementAttributeTemplate.LookupId:
		modelName = "Lookup Element Attribute Template"
		del form.unitOfMeasurement
	else:
		modelName = "Element Attribute Template"
		del form.lookup

	# Edit an existing elementAttributeTemplate.
	if form.validate_on_submit():
		oldElementAttributeTemplateName = elementAttributeTemplate.Name
		elementAttributeTemplate.Description = form.description.data
		elementAttributeTemplate.ElementTemplateId = form.elementTemplateId.data
		elementAttributeTemplate.Name = form.name.data

		if elementAttributeTemplate.LookupId:
			elementAttributeTemplate.Lookup = form.lookup.data
		else:
			elementAttributeTemplate.UnitOfMeasurement = form.unitOfMeasurement.data

		db.session.commit()
		flash('You have successfully edited the element attribute template "{}".'.format(elementAttributeTemplate.Name), "alert alert-success")
		for element in elementAttributeTemplate.ElementTemplate.Elements:
			if element.isManaged():
				# Tag management.
				newTagName = "{}_{}".format(element.Name, elementAttributeTemplate.Name.replace(" ", ""))
				oldTagName = "{}_{}".format(element.Name, oldElementAttributeTemplateName.replace(" ", ""))
				oldTag = Tag.query.filter_by(AreaId = element.TagAreaId, Name = oldTagName).one_or_none()
				if oldTag is None:
					# Old tag doesn't exist.
					newTag = Tag.query.filter_by(AreaId = element.TagAreaId, Name = newTagName).one_or_none()
					if newTag is None:
						# New tag doesn't exist, so create it.
						tag = Tag(AreaId = element.TagAreaId, LookupId = elementAttributeTemplate.LookupId, Name = newTagName,
							UnitOfMeasurementId = elementAttributeTemplate.UnitOfMeasurementId)
						db.session.add(tag)
						db.session.commit()
						elementAttributeTagId = tag.TagId
					else:
						# New tag exists, so update LookupId and UnitOfMeasurementId just in case.
						newTag.LookupId = elementAttributeTemplate.LookupId
						newTag.UnitOfMeasurementId = elementAttributeTemplate.UnitOfMeasurementId
						elementAttributeTagId = newTag.TagId
						db.session.commit()
				else:
					# Old tag exists, so update LookupId, Name and UnitOfMeasurementId just in case.
					oldTag.LookupId = elementAttributeTemplate.LookupId
					oldTag.Name = newTagName
					oldTag.UnitOfMeasurementId = elementAttributeTemplate.UnitOfMeasurementId
					elementAttributeTagId = oldTag.TagId
					db.session.commit()

				# Element attribute management.
				elementAttribute = ElementAttribute.query.filter_by(ElementAttributeTemplateId = elementAttributeTemplate.ElementAttributeTemplateId,
					ElementId = element.ElementId).one_or_none()
				if elementAttribute is None:
					# The element attribute doesn't exist, so create it.
					elementAttribute = ElementAttribute(ElementAttributeTemplateId = elementAttributeTemplate.ElementAttributeTemplateId, 
						ElementId = element.ElementId, TagId = elementAttributeTagId)
					db.session.add(elementAttribute)
				else:
					# The element attribute exists, so update TagId just in case.
					elementAttribute.TagId = elementAttributeTagId

				db.session.commit()

		return redirect(form.requestReferrer.data)

	# Present a form to edit an existing elementAttributeTemplate.
	form.elementAttributeTemplateId.data = elementAttributeTemplate.ElementAttributeTemplateId
	form.description.data = elementAttributeTemplate.Description
	form.elementTemplateId.data = elementAttributeTemplate.ElementTemplateId
	form.name.data = elementAttributeTemplate.Name
	if elementAttributeTemplate.LookupId:
		form.lookup.data = elementAttributeTemplate.Lookup
	else:
		form.unitOfMeasurement.data = elementAttributeTemplate.UnitOfMeasurement

	if form.requestReferrer.data is None:
		form.requestReferrer.data = request.referrer

	breadcrumbs = [{"url" : url_for("elements.selectElement", selectedClass = "Root"),"text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
		{"url" : url_for("elements.selectElement", selectedClass = "Enterprise",
			selectedId = elementAttributeTemplate.ElementTemplate.Site.Enterprise.EnterpriseId),
			"text" : elementAttributeTemplate.ElementTemplate.Site.Enterprise.Name},
		{"url" : url_for("elements.selectElement", selectedClass = "Site", selectedId = elementAttributeTemplate.ElementTemplate.Site.SiteId),
			"text" : elementAttributeTemplate.ElementTemplate.Site.Name},
		{"url" : url_for("elements.selectElement", selectedClass = "ElementAttributeTemplate",
			selectedId = elementAttributeTemplate.ElementTemplate.ElementTemplateId),
			"text" : elementAttributeTemplate.ElementTemplate.Name},
		{"url" : None, "text" : elementAttributeTemplate.Name}]
	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)
