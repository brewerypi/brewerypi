from flask import flash, jsonify, request, render_template
from flask_login import login_required
from sqlalchemy import and_, or_
from . import eventFrameAttributes
from .. import db
from .. decorators import adminRequired
from .. models import Area, Element, Enterprise, EventFrame, EventFrameAttribute, EventFrameAttributeTemplate, EventFrameTemplate, Site, Tag

@eventFrameAttributes.route("/eventFrameAttributes/<int:eventFrameId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def listEventFrameAttributes(eventFrameId):
	eventFrame = EventFrame.query.get_or_404(eventFrameId)
	eventFrameTemplate = EventFrameTemplate.query.get_or_404(eventFrame.EventFrameTemplate.EventFrameTemplateId)
	eventFrameTemplateIds = []
	for descendantEventFrameTemplate in eventFrameTemplate.descendants([], 0):
		eventFrameTemplateIds.append(descendantEventFrameTemplate["eventFrameTemplate"].EventFrameTemplateId)
	eventFrameAttributeTemplates = EventFrameAttributeTemplate.query.join(EventFrameTemplate, EventFrame). \
		outerjoin(EventFrameAttribute, and_(EventFrame.ElementId == EventFrameAttribute.ElementId, \
		EventFrameAttributeTemplate.EventFrameAttributeTemplateId == EventFrameAttribute.EventFrameAttributeTemplateId)). \
		filter(EventFrameTemplate.EventFrameTemplateId.in_(eventFrameTemplateIds))
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
