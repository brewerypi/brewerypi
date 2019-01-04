import csv
import os
from flask import current_app, jsonify, render_template, request, send_file
from flask_login import login_required
from sqlalchemy import and_, or_
from . import elementAttributes
from . forms import ElementAttributeImportForm
from .. import db
from .. decorators import adminRequired
from .. models import Area, ElementAttributeTemplate, Element, ElementAttribute, ElementTemplate, Enterprise, Site, Tag

@elementAttributes.route("/elementAttributes/<int:elementId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def listElementAttributes(elementId):
	element = Element.query.get_or_404(elementId)
	elementAttributeTemplates = ElementAttributeTemplate.query.join(ElementTemplate, Element). \
		outerjoin(ElementAttribute, and_(Element.ElementId == ElementAttribute.ElementId, \
		ElementAttributeTemplate.ElementAttributeTemplateId == ElementAttribute.ElementAttributeTemplateId)).filter(Element.ElementId == elementId)
	tags = Tag.query.join(Area, Site, Enterprise).order_by(Enterprise.Abbreviation, Site.Abbreviation, Area.Abbreviation, Tag.Name)
	return render_template("elementAttributes/elementAttributes.html", element = element, elementAttributeTemplates = elementAttributeTemplates, tags = tags)

@elementAttributes.route("/elementAttributes/export")
@login_required
@adminRequired
def exportElementAttributes():
	elementAttributes = ElementAttribute.query.join(Element, Tag, ElementTemplate, Site, Enterprise). \
		join(ElementAttributeTemplate, ElementAttribute.ElementAttributeTemplateId == ElementAttributeTemplate.ElementAttributeTemplateId). \
		order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, Element.Name, ElementAttributeTemplate.Name)
	with open(os.path.join(current_app.config["EXPORT_FOLDER"], current_app.config["EXPORT_ELEMENT_ATTRIBUTES_FILENAME"]), "w", encoding = "latin-1") \
		as elementsFile:
		fieldnames = ["Selected", "Element Attribute Id", "Enterprise", "Site", "Element Template", "Element", "Element Attribute Template", "Area",
			"Tag"]
		elementAttributesWriter = csv.DictWriter(elementsFile, fieldnames = fieldnames, lineterminator = "\n")
		elementAttributesWriter.writeheader()
		
		for elementAttribute in elementAttributes:
			elementAttributesWriter.writerow({"Selected" : "", "Element Attribute Id" : elementAttribute.ElementAttributeId,
			"Enterprise" : elementAttribute.Element.ElementTemplate.Site.Enterprise.Abbreviation,
			"Site" : elementAttribute.Element.ElementTemplate.Site.Abbreviation, "Element Template" : elementAttribute.Element.ElementTemplate.Name,
			"Element" : elementAttribute.Element.Name, "Element Attribute Template" : elementAttribute.ElementAttributeTemplate.Name,
			"Area" : elementAttribute.Tag.Area.Abbreviation, "Tag" : elementAttribute.Tag.Name})
	
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
				"Element Template" not in elementAttributesReader.fieldnames or "Element" not in elementAttributesReader.fieldnames or \
				"Element Attribute Template" not in elementAttributesReader.fieldnames or "Area" not in elementAttributesReader.fieldnames or \
				"Tag" not in elementAttributesReader.fieldnames:
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
					elementName = row["Element"].strip()
					elementAttributeTemplateName = row["Element Attribute Template"].strip()
					areaAbbreviation = row["Area"].strip()
					tagName = row["Tag"].strip()

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
						element = Element(Description = "", ElementTemplate = elementTemplate, Name = elementName)
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

@elementAttributes.route("/elementAttributes/updateMultiple/<int:elementId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def updateMultiple(elementId):
	# Get the data, loop through it and add new value.
	data = request.get_json(force = True)
	count = 0
	for item in data:
		elementAttributeTemplateId = item["ElementAttributeTemplateId"]
		tagId = item["TagId"]
		elementAttribute = ElementAttribute.query.filter_by(ElementAttributeTemplateId = elementAttributeTemplateId, ElementId = elementId).first()
		if elementAttribute:
			if tagId == "-1":
				# Delete.
				elementAttribute.delete()
				count = count + 1
			else:
				if str(elementAttribute.TagId) != tagId:
					# Update tag id.
					elementAttribute.TagId = tagId
					count = count + 1
		else:
			if tagId != "-1":
				# Create new.
				elementAttribute = ElementAttribute(ElementAttributeTemplateId = elementAttributeTemplateId, ElementId = elementId, TagId = tagId)
				db.session.add(elementAttribute)
				count = count + 1

	if count > 0:
		db.session.commit()
		alert = "alert alert-success"
		message = "You have successfully added or updated one or more element attributes."
	else:
		alert = "alert alert-warning"
		message = "Nothing updated to save."
	return jsonify(alert = alert, message = message)
