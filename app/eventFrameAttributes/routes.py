import csv
import os
from flask import current_app, flash, jsonify, render_template, request, send_file
from flask_login import login_required
from sqlalchemy import and_
from . import eventFrameAttributes
from . forms import EventFrameAttributeImportForm
from .. import db
from .. decorators import adminRequired
from .. models import Area, Element, ElementTemplate, Enterprise, EventFrame, EventFrameAttribute, EventFrameAttributeTemplate, EventFrameTemplate, Site, Tag

@eventFrameAttributes.route("/eventFrameAttributes/export")
@login_required
@adminRequired
def exportEventFrameAttributes():
	eventFrameAttributes = EventFrameAttribute.query.join(Element, EventFrameAttributeTemplate, Tag, ElementTemplate, Site, Enterprise). \
	join(EventFrameTemplate, and_(ElementTemplate.ElementTemplateId == EventFrameTemplate.ElementTemplateId,
		EventFrameAttributeTemplate.EventFrameTemplateId == EventFrameTemplate.EventFrameTemplateId)). \
	join(Area, and_(Site.SiteId == Area.SiteId, Tag.AreaId == Area.AreaId)). \
	order_by(Enterprise.Name, Site.Name, ElementTemplate.Name, EventFrameTemplate.Name, Element.Name, EventFrameAttributeTemplate.Name, Area.Abbreviation,
		Tag.Name)
	with open(os.path.join(current_app.config["EXPORT_FOLDER"], current_app.config["EXPORT_EVENT_FRAME_ATTRIBUTES_FILENAME"]), "w", encoding = "latin-1") \
		as eventFramesFile:
		fieldnames = ["Selected", "Event Frame Attribute Id", "Enterprise", "Site", "Element Template", "Event Frame Template", "Element",
			"Event Frame Attribute Template", "Area", "Tag"]
		eventFrameAttributesWriter = csv.DictWriter(eventFramesFile, fieldnames = fieldnames, lineterminator = "\n")
		eventFrameAttributesWriter.writeheader()
		
		for eventFrameAttribute in eventFrameAttributes:
			eventFrameAttributesWriter.writerow({"Selected" : "", "Event Frame Attribute Id" : eventFrameAttribute.EventFrameAttributeId,
			"Enterprise" : eventFrameAttribute.EventFrameAttributeTemplate.EventFrameTemplate.ElementTemplate.Site.Enterprise.Abbreviation,
			"Site" : eventFrameAttribute.EventFrameAttributeTemplate.EventFrameTemplate.ElementTemplate.Site.Abbreviation, 
			"Element Template" : eventFrameAttribute.EventFrameAttributeTemplate.EventFrameTemplate.ElementTemplate.Name,
			"Event Frame Template" : eventFrameAttribute.EventFrameAttributeTemplate.EventFrameTemplate.Name,
			"Element" : eventFrameAttribute.Element.Name, "Event Frame Attribute Template" : eventFrameAttribute.EventFrameAttributeTemplate.Name,
			"Area" : eventFrameAttribute.Tag.Area.Abbreviation, "Tag" : eventFrameAttribute.Tag.Name})
	
	return send_file(os.path.join("..", current_app.config["EXPORT_FOLDER"], current_app.config["EXPORT_EVENT_FRAME_ATTRIBUTES_FILENAME"]),
		as_attachment = True)

@eventFrameAttributes.route("/eventFrameAttributes/import", methods = ["GET", "POST"])
@login_required
@adminRequired
def importEventFrameAttributes():
	form = EventFrameAttributeImportForm()
	errors = []
	successes = []
	warnings = []

	if form.validate_on_submit():
		# Save a version of the uploaded file.
		eventFrameAttributesFile = form.eventFrameAttributesFile.data
		eventFrameAttributesFile.save(os.path.join(current_app.config["IMPORT_FOLDER"], current_app.config["IMPORT_EVENT_FRAME_ATTRIBUTES_FILENAME"]))
		eventFrameAttributesFile.close()

		# Open the uploaded file.
		with open(os.path.join(current_app.config["IMPORT_FOLDER"], current_app.config["IMPORT_EVENT_FRAME_ATTRIBUTES_FILENAME"]), "r", encoding = "latin-1") \
			as eventFrameAttributesFile:
			eventFrameAttributesReader = csv.DictReader(eventFrameAttributesFile, delimiter = ",")

			# Make sure that the header is well formed.
			if "Selected" not in eventFrameAttributesReader.fieldnames or "Event Frame Attribute Id" not in eventFrameAttributesReader.fieldnames or \
				"Enterprise" not in eventFrameAttributesReader.fieldnames or "Site" not in eventFrameAttributesReader.fieldnames or \
				"Element Template" not in eventFrameAttributesReader.fieldnames or "Event Frame Template" not in eventFrameAttributesReader.fieldnames or \
				"Element" not in eventFrameAttributesReader.fieldnames or "Event Frame Attribute Template" not in eventFrameAttributesReader.fieldnames or \
				"Area" not in eventFrameAttributesReader.fieldnames or "Tag" not in eventFrameAttributesReader.fieldnames:
				errors.append("Header malformed. Aborting upload.")
			else:
				# Iterate through each row.
				for n, row in enumerate(eventFrameAttributesReader, start = 1):
					rowNumber = n + 1
					selected = row["Selected"].strip()
					eventFrameAttributeId = row["Event Frame Attribute Id"].strip()
					enterpriseAbbreviation = row["Enterprise"].strip()
					siteAbbreviation = row["Site"].strip()
					elementTemplateName = row["Element Template"].strip()
					eventFrameTemplateName = row["Event Frame Template"].strip()
					elementName = row["Element"].strip()
					eventFrameAttributeTemplateName = row["Event Frame Attribute Template"].strip()
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

					eventFrameTemplate = EventFrameTemplate.query. \
						filter(EventFrameTemplate.Name == eventFrameTemplateName, EventFrameTemplate.ElementTemplateId == elementTemplate.ElementTemplateId). \
						first()
					if eventFrameTemplate is None:
						errors.append("Event Frame Template \"{}\" does not exist in site \"{}\". Skipping row {}.".format(eventFrameTemplateName, site.Name,
							str(rowNumber)))
						continue

					eventFrameAttributeTemplate = EventFrameAttributeTemplate.query. \
						filter(EventFrameAttributeTemplate.Name == eventFrameAttributeTemplateName,
							EventFrameAttributeTemplate.EventFrameTemplateId == eventFrameTemplate.EventFrameTemplateId).first()
					if eventFrameAttributeTemplate is None:
						errors.append("Event Frame Attribute Template \"{}\" does not exist in site \"{}\". Skipping row {}.". \
							format(eventFrameAttributeTemplateName, site.Name, str(rowNumber)))
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

					if "" == eventFrameAttributeId:
						# Check for existing event frame attribute.
						eventFrameAttribute = EventFrameAttribute.query. \
							filter(EventFrameAttribute.ElementId == element.ElementId,
								EventFrameAttribute.EventFrameAttributeTemplateId == eventFrameAttributeTemplate.EventFrameAttributeTemplateId).first()
						if eventFrameAttribute is not None:
							warnings.append("Event Frame Attribute Template \"{}\" already exists for Element \"{}\". Skipping row {}.". \
								format(eventFrameAttributeTemplateName, elementName, str(rowNumber)))
							continue

						# Add event frame attribute.
						eventFrameAttribute = EventFrameAttribute(Element = element, EventFrameAttributeTemplate = eventFrameAttributeTemplate, Tag = tag)
						db.session.add(eventFrameAttribute)
						db.session.commit()
						successes.append("Element Attribute Template \"{}\" added to Element \"{}\".".format(eventFrameAttributeTemplateName, elementName))
					else:
						# Edit event frame attribute.
						eventFrameAttribute = EventFrameAttribute.query.get_or_404(eventFrameAttributeId)

						# The element and/or event frame attribute template have changed. Check for existing event frame attribute.
						if eventFrameAttribute.ElementId != element.ElementId or \
							eventFrameAttribute.EventFrameAttributeTemplateId != eventFrameAttributeTemplate.EventFrameAttributeTemplateId:
							eventFrameAttributeCheck = EventFrameAttribute.query.join(Element, EventFrameAttributeTemplate). \
								filter(EventFrameAttribute.ElementId == element.ElementId,
									EventFrameAttribute.EventFrameAttributeTemplateId == eventFrameAttributeTemplate.EventFrameAttributeTemplateId).first()
							if eventFrameAttributeCheck is not None:
								warnings.append("Event Frame Attribute Template  \"{}\" already exists for Element \"{}\". Skipping row {}.". \
									format(eventFrameAttributeName, elementName, str(rowNumber)))
								continue
								
						eventFrameAttribute.EventFrameAttributeTemplate = eventFrameAttributeTemplate
						eventFrameAttribute.Element = element
						eventFrameAttribute.Tag = tag
						db.session.commit()
						successes.append("Event Frame Attribute Template \"{}\" updated for Element \"{}\".".format(eventFrameAttributeTemplateName,
							elementName))

	return render_template("import.html", errors = errors, form = form, importing = "Event Frame Attributes", successes = successes, warnings = warnings)
	
@eventFrameAttributes.route("/eventFrameAttributes/<int:eventFrameId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def listEventFrameAttributes(eventFrameId):
	eventFrame = EventFrame.query.get_or_404(eventFrameId)
	eventFrameTemplate = EventFrameTemplate.query.get_or_404(eventFrame.EventFrameTemplate.EventFrameTemplateId)
	eventFrameTemplateIds = []
	for descendantEventFrameTemplate in eventFrameTemplate.descendants([], 0):
		eventFrameTemplateIds.append(descendantEventFrameTemplate["eventFrameTemplate"].EventFrameTemplateId)
	eventFrameAttributeTemplates = EventFrameAttributeTemplate.query.filter(EventFrameAttributeTemplate.EventFrameTemplateId.in_(eventFrameTemplateIds))
	tags = Tag.query.join(Area, Site, Enterprise).order_by(Enterprise.Abbreviation, Site.Abbreviation, Area.Abbreviation, Tag.Name)
	return render_template("eventFrameAttributes/eventFrameAttributes.html", eventFrame = eventFrame,
		eventFrameAttributeTemplates = eventFrameAttributeTemplates, tags = tags)

@eventFrameAttributes.route("/eventFrameAttributes/updateMultiple/<int:eventFrameId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def updateMultiple(eventFrameId):
	# Get the data, loop through it and add new value.
	data = request.get_json(force = True)
	eventFrame = EventFrame.query.get_or_404(eventFrameId)
	count = 0
	for item in data:
		eventFrameAttributeTemplateId = item["EventFrameAttributeTemplateId"]
		tagId = item["TagId"]
		eventFrameAttribute = EventFrameAttribute.query. \
			filter_by(ElementId = eventFrame.ElementId, EventFrameAttributeTemplateId = eventFrameAttributeTemplateId).first()
		if eventFrameAttribute:
			if tagId == "-1":
				# Delete.
				db.session.delete(eventFrameAttribute)
				count = count + 1
			else:
				if str(eventFrameAttribute.TagId) != tagId:
					# Update tag id.
					eventFrameAttribute.TagId = tagId
					count = count + 1
		else:
			if tagId != "-1":
				# Create new.
				eventFrameAttribute = EventFrameAttribute(ElementId = eventFrame.ElementId,
					EventFrameAttributeTemplateId = eventFrameAttributeTemplateId, TagId = tagId)
				db.session.add(eventFrameAttribute)
				count = count + 1

	if count > 0:
		db.session.commit()
		message = "You have successfully added or updated one or more element attributes."
		flash(message, "alert alert-success")
	else:
		message = "Nothing updated to save."
		flash(message, "alert alert-warning")
	return jsonify({"response": message})
