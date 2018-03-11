import csv
import os
from flask import current_app, flash, redirect, render_template, send_file, url_for
from sqlalchemy import or_
from . import elementAttributes
from . forms import ElementAttributeForm, ElementAttributeImportForm, ElementAttributeValueForm
from .. import db
from .. decorators import adminRequired
from .. models import Area, AttributeTemplate, Element, ElementAttribute, ElementTemplate, Enterprise, LookupValue, Site, Tag, TagValue
from .. tagValues . forms import TagValueForm

@elementAttributes.route("/elementAttributes", methods = ["GET", "POST"])
@adminRequired
def listElementAttributes():
	elementAttributes = ElementAttribute.query.all()
	return render_template("elementAttributes/elementAttributes.html", elementAttributes = elementAttributes)

@elementAttributes.route("/elementAttributes/add", methods = ["GET", "POST"])
@adminRequired
def addElementAttribute():
	modelName = "Element Attribute"
	operation = "Add"
	form = ElementAttributeForm()

	# Add a new element attribute.
	if form.validate_on_submit():
		elementAttribute = ElementAttribute(AttributeTemplate = form.attributeTemplate.data, Element = form.element.data, Tag = form.tag.data)
		db.session.add(elementAttribute)
		db.session.commit()
		flash("You have successfully added the element attribute \"" + form.attributeTemplate.data.Name + "\" for \"" + form.element.data.Name + "\".",
			"alert alert-success")
		return redirect(url_for("elementAttributes.listElementAttributes"))

	# Present a form to add a new element attribute.
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@elementAttributes.route("/elementAttributes/delete/<int:elementAttributeId>", methods = ["GET", "POST"])
@adminRequired
def deleteElementAttribute(elementAttributeId):
	elementAttribute = ElementAttribute.query.get_or_404(elementAttributeId)
	attributeTemplateName = elementAttribute.AttributeTemplate.Name
	elementName = elementAttribute.Element.Name
	db.session.delete(elementAttribute)
	db.session.commit()
	flash("You have successfully deleted the element attribute \"" + attributeTemplateName + "\" for \"" + elementName + "\".", "alert alert-success")
	return redirect(url_for("elementAttributes.listElementAttributes"))

@elementAttributes.route("/elementAttributes/edit/<int:elementAttributeId>", methods = ["GET", "POST"])
@adminRequired
def editElementAttribute(elementAttributeId):
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
			elementAttribute.Element.Name + "\".", "alert alert-success")
		return redirect(url_for("elementAttributes.listElementAttributes"))

	# Present a form to edit an existing element attribute.
	form.attributeTemplate.data = elementAttribute.AttributeTemplate
	form.element.data = elementAttribute.Element
	form.tag.data = elementAttribute.Tag
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@elementAttributes.route("/elementAttributes/export")
@adminRequired
def exportElementAttributes():
	elementAttributes = ElementAttribute.query.join(Element, Tag, ElementTemplate, Site, Enterprise). \
		join(AttributeTemplate, ElementAttribute.AttributeTemplateId == AttributeTemplate.AttributeTemplateId). \
		order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, Element.Name, AttributeTemplate.Name)
	with open(os.path.join(current_app.config["EXPORT_FOLDER"], current_app.config["EXPORT_ELEMENT_ATTRIBUTES_FILENAME"]), "w", encoding = "latin-1") \
		as elementsFile:
		fieldnames = ["Selected", "Element Attribute Id", "Enterprise", "Site", "Element Template", "Element Name", "Attribute Template", "Area", "Tag Name"]
		elementAttributesWriter = csv.DictWriter(elementsFile, fieldnames = fieldnames, lineterminator = "\n")
		elementAttributesWriter.writeheader()
		
		for elementAttribute in elementAttributes:
			elementAttributesWriter.writerow({"Selected" : "", "Element Attribute Id" : elementAttribute.ElementAttributeId, \
			"Enterprise" : elementAttribute.Element.ElementTemplate.Site.Enterprise.Abbreviation, \
			"Site" : elementAttribute.Element.ElementTemplate.Site.Abbreviation, "Element Template" : elementAttribute.Element.ElementTemplate.Name, \
			"Element Name" : elementAttribute.Element.Name, "Attribute Template" : elementAttribute.AttributeTemplate.Name, \
			"Area" : elementAttribute.Tag.Area.Abbreviation, "Tag Name" : elementAttribute.Tag.Name})
	
	return send_file(os.path.join("..", current_app.config["EXPORT_FOLDER"], current_app.config["EXPORT_ELEMENT_ATTRIBUTES_FILENAME"]), as_attachment = True)

@elementAttributes.route("/elementAttributes/import", methods = ["GET", "POST"])
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
				"Attribute Template" not in elementAttributesReader.fieldnames or "Area" not in elementAttributesReader.fieldnames or \
				"Tag Name" not in elementAttributesReader.fieldnames:
				errors.append("Header malformed. Aborting upload.")
				return render_template("elementAttributes/importElementAttributes.html", errors = errors, form = form)

			# Iterate through each row.
			for n, row in enumerate(elementAttributesReader, start = 1):
				rowNumber = n + 1
				selected = row["Selected"].strip()
				elementAttributeId = row["Element Attribute Id"].strip()
				enterpriseAbbreviation = row["Enterprise"].strip()
				siteAbbreviation = row["Site"].strip()
				elementTemplateName = row["Element Template"].strip()
				elementName = row["Element Name"].strip()
				attributeTemplateName = row["Attribute Template"].strip()
				areaAbbreviation = row["Area"].strip()
				tagName = row["Tag Name"].strip()

				# Skip rows that are now selected.
				if "" == selected:
					warnings.append("Row " + str(rowNumber) + " not selected. Skipping row " + str(rowNumber) + ".")
					continue

				enterprise = Enterprise.query.filter(Enterprise.Abbreviation == enterpriseAbbreviation).first()
				if enterprise is None:
					errors.append("Enterprise \"" + enterpriseAbbreviation + "\" does not exist. Skipping row " + str(rowNumber) + ".")
					continue

				site = Site.query.filter(Site.Abbreviation == siteAbbreviation, Site.EnterpriseId == enterprise.EnterpriseId).first()
				if site is None:
					errors.append("Site \"" + siteAbbreviation + "\" does not exist. Skipping row " + str(rowNumber) + ".")
					continue

				elementTemplate = ElementTemplate.query.filter(ElementTemplate.Name == elementTemplateName, ElementTemplate.SiteId == site.SiteId).first()
				if elementTemplate is None:
					errors.append("Element Template \"" + elementTemplateName + "\" does not exist in site \"" + site.Name + "\". Skipping row " + \
						str(rowNumber) + ".")
					continue

				attributeTemplate = AttributeTemplate.query.filter(AttributeTemplate.ElementTemplateId == elementTemplate.ElementTemplateId, \
					AttributeTemplate.Name == attributeTemplateName).first()
				if attributeTemplate is None:
					errors.append("Attribute Template \"" + attributeTemplateName + "\" does not exist in site \"" + site.Name + "\". Skipping row " + \
						str(rowNumber) + ".")
					continue

				area = Area.query.filter(Area.Abbreviation == areaAbbreviation, Area.SiteId == site.SiteId).first()
				if area is None:
					errors.append("Area \"" + areaAbbreviation + "\" does not exist. Skipping row " + str(rowNumber) + ".")
					continue

				tag = Tag.query.filter(Tag.AreaId == area.AreaId, Tag.Name == tagName).first()
				if tag is None:
					errors.append("Tag \"" + tagName + "\" does not exist in area \"" + area.Name + "\". Skipping row " + str(rowNumber) + ".")
					continue

				element = Element.query.filter(Element.ElementTemplateId == elementTemplate.ElementTemplateId, Element.Name == elementName).first()
				if element is None:
					# Add element.
					element = Element(ElementTemplate = elementTemplate, Name = elementName)
					db.session.add(element)
					db.session.commit()
					successes.append("Element \"" + elementName + "\" added.")

				if "" == elementAttributeId:
					# Add element attribute.
					# Check for existing element attribute.
					elementAttribute = ElementAttribute.query.filter(ElementAttribute.AttributeTemplateId == attributeTemplate.AttributeTemplateId, \
						ElementAttribute.ElementId == element.ElementId).first()
					if elementAttribute is not None:
						warnings.append("Attribute Template \"" + attributeTemplateName + "\" already exists for Element \"" + elementName + \
							"\". Skipping row " + str(rowNumber) + ".")
						continue

					# Add element attribute.
					elementAttribute = ElementAttribute(AttributeTemplate = attributeTemplate, Element = element, Tag = tag)
					db.session.add(elementAttribute)
					db.session.commit()
					successes.append("Attribute Template \"" + attributeTemplateName + "\" added to Element \"" + elementName + "\".")
				else:
					# Edit element attribute.
					elementAttribute = ElementAttribute.query.get_or_404(elementAttributeId)

					# The attribute template and/or element have changed. Check for existing element attribute.
					if elementAttribute.AttributeTemplateId != attributeTemplate.AttributeTemplateId or elementAttribute.ElementId != element.ElementId:
						elementAttributeCheck = ElementAttribute.query.join(AttributeTemplate, Element). \
							filter(ElementAttribute.AttributeTemplateId == attributeTemplate.AttributeTemplateId, \
							ElementAttribute.ElementId == element.ElementId).first()
						if elementAttributeCheck is not None:
							warnings.append("Attribute Template  \"" + elementAttributeName + "\" already exists for Element \"" + elementName + \
								"\". Skipping row " + str(rowNumber) + ".")
							continue
							
					elementAttribute.AttributeTemplate = attributeTemplate
					elementAttribute.Element = element
					elementAttribute.Tag = tag
					db.session.commit()
					successes.append("Attribute Template \"" + attributeTemplateName + "\" updated for Element \"" + elementName + "\".")

	return render_template("import.html", errors = errors, form = form, importing = "Element Attributes", successes = successes, warnings = warnings)

@elementAttributes.route("/elementAttributes/addValue/<int:elementId>/<int:tagId>", methods = ["GET", "POST"])
@adminRequired
def addElementAttributeValue(elementId, tagId):
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
		flash("You have successfully added a new element attribute value.", "alert alert-success")
		return redirect(url_for("elements.dashboard", elementId = elementId))

	# Present a form to add a new element attribute value.
	form.tagId.data = tag.TagId
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@elementAttributes.route("/elementAttributes/deleteValue/<int:elementId>/<int:tagValueId>", methods = ["GET", "POST"])
@adminRequired
def deleteElementAttributeValue(elementId, tagValueId):
	tagValue = TagValue.query.get_or_404(tagValueId)
	db.session.delete(tagValue)
	db.session.commit()
	flash("You have successfully deleted the element attribute value.", "alert alert-success")
	return redirect(url_for("elements.dashboard", elementId = elementId))

@elementAttributes.route("/elementAttributes/editValue/<int:elementId>/<int:tagValueId>", methods = ["GET", "POST"])
@adminRequired
def editElementAttributeValue(elementId, tagValueId):
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
		flash("You have successfully edited the element attribute value.", "alert alert-success")
		return redirect(url_for("elements.dashboard", elementId = elementId))

	# Present a form to edit an existing element attribute value.
	form.tagId.data = tagValue.TagId
	form.timestamp.data = tagValue.Timestamp

	if tag.LookupId:
		form.lookupValue.data = tagValue.Value
	else:
		form.value.data = tagValue.Value

	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)
