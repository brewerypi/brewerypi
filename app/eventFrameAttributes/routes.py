import csv
import os
from flask import current_app, flash, jsonify, redirect, render_template, request, send_file
from flask_login import login_required
from sqlalchemy import and_
from . import eventFrameAttributes
from .. import db
from .. decorators import adminRequired
from .. models import Area, Element, ElementTemplate, Enterprise, EventFrameAttribute, EventFrameAttributeTemplate, EventFrameTemplate, Site, Tag

@eventFrameAttributes.route("/eventFrameAttributes/export")
@login_required
@adminRequired
def exportEventFrameAttributes():
	# elementAttributes = ElementAttribute.query.join(Element, Tag, ElementTemplate, Site, Enterprise). \
	# 	join(ElementAttributeTemplate, ElementAttribute.ElementAttributeTemplateId == ElementAttributeTemplate.ElementAttributeTemplateId). \
	# 	order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, Element.Name, ElementAttributeTemplate.Name)
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
