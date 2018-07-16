import csv
import os
from flask import current_app, flash, redirect, render_template, request, send_file, url_for
from flask_login import login_required
from sqlalchemy import or_
from . import elementAttributes
from . forms import ElementAttributeForm, ElementAttributeImportForm
from .. import db
from .. decorators import adminRequired
from .. models import Area, ElementAttributeTemplate, Element, ElementAttribute, ElementTemplate, Enterprise, Site, Tag

@elementAttributes.route("/elementAttributes/<int:elementId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def listElementAttributes(elementId):
	element = Element.query.get_or_404(elementId)
	return render_template("elementAttributes/elementAttributes.html", element = element)

@elementAttributes.route("/elementAttributes/add/<int:elementId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def addElementAttribute(elementId):
	modelName = "Element Attribute"
	operation = "Add"
	form = ElementAttributeForm()
	element = Element.query.get_or_404(elementId)
	form.elementAttributeTemplate.query = ElementAttributeTemplate.query.join(ElementTemplate, Site, Enterprise). \
		filter(ElementAttributeTemplate.ElementTemplateId == element.ElementTemplateId). \
		order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, ElementAttributeTemplate.Name)

	# Add a new element attribute.
	if form.validate_on_submit():
		elementAttribute = ElementAttribute(ElementAttributeTemplate = form.elementAttributeTemplate.data, ElementId = form.elementId.data, Tag = form.tag.data)
		db.session.add(elementAttribute)
		db.session.commit()
		flash("You have successfully added the element attribute \"{}\" for \"{}\".".format(elementAttribute.ElementAttributeTemplate.Name, element.Name),
			"alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to add a new element attribute.
	form.elementId.data = elementId
	form.requestReferrer.data = request.referrer
	breadcrumbs = [{"url" : url_for("elements.selectElement", selectedClass = "Root"), "text" : ".."},
		{"url" : url_for("elements.selectElement", selectedClass = "Enterprise", selectedId = element.ElementTemplate.Site.Enterprise.EnterpriseId),
			"text" : element.ElementTemplate.Site.Enterprise.Name},
		{"url" : url_for("elements.selectElement", selectedClass = "Site", selectedId = element.ElementTemplate.Site.SiteId),
			"text" : element.ElementTemplate.Site.Name},
		{"url" : url_for("elements.selectElement", selectedClass = "ElementTemplate", selectedId = element.ElementTemplate.ElementTemplateId),
			"text" : element.ElementTemplate.Name},
		{"url" : url_for("elementAttributes.listElementAttributes", elementId = elementId), "text" : element.Name}]
	return render_template("addEditModel.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@elementAttributes.route("/elementAttributes/delete/<int:elementAttributeId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def deleteElementAttribute(elementAttributeId):
	elementAttribute = ElementAttribute.query.get_or_404(elementAttributeId)
	elementAttributeTemplateName = elementAttribute.ElementAttributeTemplate.Name
	elementName = elementAttribute.Element.Name
	db.session.delete(elementAttribute)
	db.session.commit()
	flash("You have successfully deleted the element attribute \"{}\" for \"{}\".".format(elementAttributeTemplateName, elementName), "alert alert-success")
	return redirect(request.referrer)

@elementAttributes.route("/elementAttributes/edit/<int:elementAttributeId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def editElementAttribute(elementAttributeId):
	modelName = "Element Attribute"
	operation = "Edit"
	elementAttribute = ElementAttribute.query.get_or_404(elementAttributeId)
	form = ElementAttributeForm(obj = elementAttribute)
	form.elementAttributeTemplate.query = ElementAttributeTemplate.query.join(ElementTemplate, Site, Enterprise). \
		filter(ElementAttributeTemplate.ElementTemplateId == elementAttribute.Element.ElementTemplateId). \
		order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, ElementAttributeTemplate.Name)

	# Edit an existing element attribute.
	if form.validate_on_submit():	
		elementAttribute.ElementAttributeTemplate = form.elementAttributeTemplate.data
		elementAttribute.ElementId = form.elementId.data
		elementAttribute.Tag = form.tag.data
		db.session.commit()
		flash("You have successfully edited the element attribute \"" + elementAttribute.ElementAttributeTemplate.Name + "\" for \"" + \
			elementAttribute.Element.Name + "\".", "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to edit an existing element attribute.
	form.elementAttributeTemplate.data = elementAttribute.ElementAttributeTemplate
	form.elementId.data = elementAttribute.ElementId
	form.tag.data = elementAttribute.Tag
	form.requestReferrer.data = request.referrer
	breadcrumbs = [{"url" : url_for("elements.selectElement", selectedClass = "Root"), "text" : ".."},
		{"url" : url_for("elements.selectElement", selectedClass = "Enterprise",
			selectedId = elementAttribute.Element.ElementTemplate.Site.Enterprise.EnterpriseId),
			"text" : elementAttribute.Element.ElementTemplate.Site.Enterprise.Name},
		{"url" : url_for("elements.selectElement", selectedClass = "Site", selectedId = elementAttribute.Element.ElementTemplate.Site.SiteId),
			"text" : elementAttribute.Element.ElementTemplate.Site.Name},
		{"url" : url_for("elements.selectElement", selectedClass = "ElementTemplate", selectedId = elementAttribute.Element.ElementTemplate.ElementTemplateId),
			"text" : elementAttribute.Element.ElementTemplate.Name},
		{"url" : url_for("elementAttributes.listElementAttributes", elementId = elementAttribute.ElementId), "text" : elementAttribute.Element.Name},
		{"url" : None, "text" : elementAttribute.ElementAttributeTemplate.Name}]
	return render_template("addEditModel.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@elementAttributes.route("/elementAttributes/export")
@login_required
@adminRequired
def exportElementAttributes():
	elementAttributes = ElementAttribute.query.join(Element, Tag, ElementTemplate, Site, Enterprise). \
		join(ElementAttributeTemplate, ElementAttribute.ElementAttributeTemplateId == ElementAttributeTemplate.ElementAttributeTemplateId). \
		order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, Element.Name, ElementAttributeTemplate.Name)
	with open(os.path.join(current_app.config["EXPORT_FOLDER"], current_app.config["EXPORT_ELEMENT_ATTRIBUTES_FILENAME"]), "w", encoding = "latin-1") \
		as elementsFile:
		fieldnames = ["Selected", "Element Attribute Id", "Enterprise", "Site", "Element Template", "Element Name", "Element Attribute Template", "Area",
			"Tag Name"]
		elementAttributesWriter = csv.DictWriter(elementsFile, fieldnames = fieldnames, lineterminator = "\n")
		elementAttributesWriter.writeheader()
		
		for elementAttribute in elementAttributes:
			elementAttributesWriter.writerow({"Selected" : "", "Element Attribute Id" : elementAttribute.ElementAttributeId, \
			"Enterprise" : elementAttribute.Element.ElementTemplate.Site.Enterprise.Abbreviation, \
			"Site" : elementAttribute.Element.ElementTemplate.Site.Abbreviation, "Element Template" : elementAttribute.Element.ElementTemplate.Name, \
			"Element Name" : elementAttribute.Element.Name, "Element Attribute Template" : elementAttribute.ElementAttributeTemplate.Name, \
			"Area" : elementAttribute.Tag.Area.Abbreviation, "Tag Name" : elementAttribute.Tag.Name})
	
	return send_file(os.path.join("..", current_app.config["EXPORT_FOLDER"], current_app.config["EXPORT_ELEMENT_ATTRIBUTES_FILENAME"]), as_attachment = True)

@elementAttributes.route("/elementAttributes/import", methods = ["GET", "POST"])
@login_required
@adminRequired
def importElementAttributes():
	form = ElementAttributeImportForm()
	errors = []
	successes = []
	warnings = []

	if form.validate_on_submit():
		# Save a version of the uploaded file.
		elementAttributesFile = form.elementAttributesFile.data
		elementAttributesFile.save(os.path.join(current_app.config["IMPORT_FOLDER"], current_app.config["IMPORT_ELEMENT_ATTRIBUTES_FILENAME"]))
		elementAttributesFile.close()

		# Open the uploaded file.
		with open(os.path.join(current_app.config["IMPORT_FOLDER"], current_app.config["IMPORT_ELEMENT_ATTRIBUTES_FILENAME"]), "r", encoding = "latin-1") \
			as elementAttributesFile:
			elementAttributesReader = csv.DictReader(elementAttributesFile, delimiter = ",")

			# Make sure that the header is well formed.
			if "Selected" not in elementAttributesReader.fieldnames or "Element Attribute Id" not in elementAttributesReader.fieldnames or \
				"Enterprise" not in elementAttributesReader.fieldnames or "Site" not in elementAttributesReader.fieldnames or \
				"Element Template" not in elementAttributesReader.fieldnames or "Element Name" not in elementAttributesReader.fieldnames or \
				"Element Attribute Template" not in elementAttributesReader.fieldnames or "Area" not in elementAttributesReader.fieldnames or \
				"Tag Name" not in elementAttributesReader.fieldnames:
				errors.append("Header malformed. Aborting upload.")
			else:
				# Iterate through each row.
				for n, row in enumerate(elementAttributesReader, start = 1):
					rowNumber = n + 1
					selected = row["Selected"].strip()
					elementAttributeId = row["Element Attribute Id"].strip()
					enterpriseAbbreviation = row["Enterprise"].strip()
					siteAbbreviation = row["Site"].strip()
					elementTemplateName = row["Element Template"].strip()
					elementName = row["Element Name"].strip()
					elementAttributeTemplateName = row["Element Attribute Template"].strip()
					areaAbbreviation = row["Area"].strip()
					tagName = row["Tag Name"].strip()

					# Skip rows that are now selected.
					if "" == selected:
						warnings.append("Row {} not selected. Skipping row {}.".format(str(rowNumber), str(rowNumber)))
						continue

					enterprise = Enterprise.query.filter(Enterprise.Abbreviation == enterpriseAbbreviation).first()
					if enterprise is None:
						errors.append("Enterprise \"{}\" does not exist. Skipping row {}.".format(enterpriseAbbreviation, str(rowNumber)))
						continue

					site = Site.query.filter(Site.Abbreviation == siteAbbreviation, Site.EnterpriseId == enterprise.EnterpriseId).first()
					if site is None:
						errors.append("Site \"{}\" does not exist. Skipping row {}.".format(siteAbbreviation, str(rowNumber)))
						continue

					elementTemplate = ElementTemplate.query.filter(ElementTemplate.Name == elementTemplateName, ElementTemplate.SiteId == site.SiteId).first()
					if elementTemplate is None:
						errors.append("Element Template \"{}\" does not exist in site \"{}\". Skipping row {}.".format(elementTemplateName, site.Name,
							str(rowNumber)))
						continue

					elementAttributeTemplate = ElementAttributeTemplate.query. \
						filter(ElementAttributeTemplate.ElementTemplateId == elementTemplate.ElementTemplateId,
						ElementAttributeTemplate.Name == elementAttributeTemplateName).first()
					if elementAttributeTemplate is None:
						errors.append("Element Attribute Template \"{}\" does not exist in site \"{}\". Skipping row {}.".format(elementAttributeTemplateName,
							site.Name, str(rowNumber)))
						continue

					area = Area.query.filter(Area.Abbreviation == areaAbbreviation, Area.SiteId == site.SiteId).first()
					if area is None:
						errors.append("Area \"{}\" does not exist. Skipping row {}.".format(areaAbbreviation, str(rowNumber)))
						continue

					tag = Tag.query.filter(Tag.AreaId == area.AreaId, Tag.Name == tagName).first()
					if tag is None:
						errors.append("Tag \"{}\" does not exist in area \"{}\". Skipping row {}.".format(tagName, area.Name, str(rowNumber)))
						continue

					element = Element.query.filter(Element.ElementTemplateId == elementTemplate.ElementTemplateId, Element.Name == elementName).first()
					if element is None:
						# Add element.
						element = Element(ElementTemplate = elementTemplate, Name = elementName)
						db.session.add(element)
						db.session.commit()
						successes.append("Element \"{}\" added.".format(elementName))

					if "" == elementAttributeId:
						# Check for existing element attribute.
						elementAttribute = ElementAttribute.query. \
							filter(ElementAttribute.ElementAttributeTemplateId == elementAttributeTemplate.ElementAttributeTemplateId,
							ElementAttribute.ElementId == element.ElementId).first()
						if elementAttribute is not None:
							warnings.append("Element Attribute Template \"{}\" already exists for Element \"{}\". Skipping row {}.". \
								format(elementAttributeTemplateName, elementName, str(rowNumber)))
							continue

						# Add element attribute.
						elementAttribute = ElementAttribute(ElementAttributeTemplate = elementAttributeTemplate, Element = element, Tag = tag)
						db.session.add(elementAttribute)
						db.session.commit()
						successes.append("Element Attribute Template \"{}\" added to Element \"{}\".".format(elementAttributeTemplateName, elementName))
					else:
						# Edit element attribute.
						elementAttribute = ElementAttribute.query.get_or_404(elementAttributeId)

						# The element attribute template and/or element have changed. Check for existing element attribute.
						if elementAttribute.ElementAttributeTemplateId != elementAttributeTemplate.ElementAttributeTemplateId or \
							elementAttribute.ElementId != element.ElementId:
							elementAttributeCheck = ElementAttribute.query.join(ElementAttributeTemplate, Element). \
								filter(ElementAttribute.ElementAttributeTemplateId == elementAttributeTemplate.ElementAttributeTemplateId, \
								ElementAttribute.ElementId == element.ElementId).first()
							if elementAttributeCheck is not None:
								warnings.append("Element Attribute Template  \"{}\" already exists for Element \"{}\". Skipping row {}.". \
									format(elementAttributeName, elementName, str(rowNumber)))
								continue
								
						elementAttribute.ElementAttributeTemplate = elementAttributeTemplate
						elementAttribute.Element = element
						elementAttribute.Tag = tag
						db.session.commit()
						successes.append("Element Attribute Template \"{}\" updated for Element \"{}\".".format(elementAttributeTemplateName, elementName))

	return render_template("import.html", errors = errors, form = form, importing = "Element Attributes", successes = successes, warnings = warnings)
