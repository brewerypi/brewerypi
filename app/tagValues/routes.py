from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_
from . import tagValues
from . forms import TagValueForm
from .. import db
from .. decorators import permissionRequired
from .. models import Area, ElementAttribute, Enterprise, EventFrame, EventFrameAttribute, Lookup, LookupValue, Permission, Site, Tag, TagValue

modelName = "Tag Value"

@tagValues.route("/tagValues/<int:tagId>", methods = ["GET", "POST"])
@tagValues.route("/tagValues/<int:tagId>/<int:months>", methods = ["GET", "POST"])
@tagValues.route("/tagValues/elementAttribute/<int:elementAttributeId>", methods = ["GET", "POST"])
@tagValues.route("/tagValues/elementAttribute/<int:elementAttributeId>/<int:months>", methods = ["GET", "POST"])
@tagValues.route("/tagValues/eventFrameAttribute/<int:eventFrameId>/<int:eventFrameAttributeId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def listTagValues(tagId = None, months = None, elementAttributeId = None, eventFrameId = None, eventFrameAttributeId = None):
	elementAttribute = None
	eventFrame = None
	eventFrameAttribute = None
	if elementAttributeId:
		elementAttribute = ElementAttribute.query.get_or_404(elementAttributeId)
		tag = Tag.query.get_or_404(elementAttribute.TagId)
	elif eventFrameId:
		eventFrame = EventFrame.query.get_or_404(eventFrameId)
		eventFrameAttribute = EventFrameAttribute.query.get_or_404(eventFrameAttributeId)
		tag = Tag.query.get_or_404(eventFrameAttribute.TagId)
	else:
		tag = Tag.query.get_or_404(tagId)

	if months is None:
		months = 3

	fromTimestamp = datetime.utcnow() - relativedelta(months = months)
	toTimestamp = datetime.utcnow()
	if tag.LookupId:
		if eventFrame:
			if eventFrame.EndTimestamp:
				tagValues = TagValue.query.join(Tag, Lookup, LookupValue).filter(Tag.TagId == tag.TagId, TagValue.Value == LookupValue.Value,
					TagValue.Timestamp >= eventFrame.StartTimestamp, TagValue.Timestamp <= eventFrame.EndTimestamp)
			else:
				tagValues = TagValue.query.join(Tag, Lookup, LookupValue).filter(Tag.TagId == tag.TagId, TagValue.Value == LookupValue.Value,
					TagValue.Timestamp >= eventFrame.StartTimestamp)
		else:
			if months == 0:
				tagValues = TagValue.query.join(Tag, Lookup, LookupValue).filter(Tag.TagId == tag.TagId, TagValue.Value == LookupValue.Value)
			else:
				tagValues = TagValue.query.join(Tag, Lookup, LookupValue).filter(Tag.TagId == tag.TagId, TagValue.Timestamp >= fromTimestamp,
					TagValue.Timestamp <= toTimestamp, TagValue.Value == LookupValue.Value)
	else:
		if eventFrame:
			if eventFrame.EndTimestamp:
				tagValues = TagValue.query.filter(TagValue.TagId == tag.TagId, TagValue.Timestamp >= eventFrame.StartTimestamp,
					TagValue.Timestamp <= eventFrame.EndTimestamp)
			else:
				tagValues = TagValue.query.filter(TagValue.TagId == tag.TagId, TagValue.Timestamp >= eventFrame.StartTimestamp)
		else:
			if months == 0:
				tagValues = TagValue.query.filter(TagValue.TagId == tag.TagId)
			else:
				tagValues = TagValue.query.filter(TagValue.TagId == tag.TagId, TagValue.Timestamp >= fromTimestamp, TagValue.Timestamp <= toTimestamp)

	return render_template("tagValues/tagValues.html", elementAttribute = elementAttribute, eventFrame = eventFrame, eventFrameAttribute = eventFrameAttribute,
		months = months, tag = tag, tagValues = tagValues)

@tagValues.route("/tagValues/addMultiple", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def addMultiple():
	# Get the data, loop through it and add new value.
	data = request.get_json(force = True)
	count = 0
	for item in data:
		tagValue = TagValue(TagId = item["tagId"], Timestamp = item["timestamp"], UserId = current_user.get_id(), Value = item["value"])
		db.session.add(tagValue)
		count = count + 1

	if count > 0:
		db.session.commit()
		message = "You have successfully added one or more new tag values."
		flash(message, "alert alert-success")
	else:
		message = "Nothing added to save."
		flash(message, "alert alert-warning")
	return jsonify({"response": message})

@tagValues.route("/tagValues/add/<int:tagId>", methods = ["GET", "POST"])
@tagValues.route("/tagValues/add/elementAttribute/<int:elementAttributeId>", methods = ["GET", "POST"])
@tagValues.route("/tagValues/add/eventFrameAttribute/<int:eventFrameId>/<int:eventFrameAttributeId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def addTagValue(tagId = None, elementAttributeId = None, eventFrameId = None, eventFrameAttributeId = None):
	operation = "Add"
	if elementAttributeId:
		elementAttribute = ElementAttribute.query.get_or_404(elementAttributeId)
		tag = Tag.query.get_or_404(elementAttribute.TagId)
	elif eventFrameId:
		eventFrameAttribute = EventFrameAttribute.query.get_or_404(eventFrameAttributeId)
		tag = Tag.query.get_or_404(eventFrameAttribute.TagId)
	else:
		tag = Tag.query.get_or_404(tagId)

	form = TagValueForm()

	# Configure the form based on if the tag value is associated with a lookup.
	if tag.LookupId:
		form.lookupValue.choices = [(lookupValue.Value, lookupValue.Name) for lookupValue in LookupValue.query. \
			filter(LookupValue.LookupId == tag.LookupId, LookupValue.Selectable == True)]
		del form.value
	else:
		del form.lookupValue

	# Add a new tag value.
	if form.validate_on_submit():
		if tag.LookupId:
			tagValue = TagValue(TagId = form.tagId.data, Timestamp = form.utcTimestamp.data, UserId = current_user.get_id(), Value = form.lookupValue.data)
		else:
			tagValue = TagValue(TagId = form.tagId.data, Timestamp = form.utcTimestamp.data, UserId = current_user.get_id(), Value = form.value.data)

		db.session.add(tagValue)
		db.session.commit()
		flash("You have successfully added a new tag value.", "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to add a new tag value.
	form.tagId.data = tag.TagId
	if form.requestReferrer.data is None:
		form.requestReferrer.data = request.referrer

	if elementAttributeId:
		breadcrumbs = [{"url" : url_for("tags.selectTag", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
			{"url" : url_for("elements.selectElement", selectedClass = "Enterprise",
				selectedId = elementAttribute.Element.ElementTemplate.Site.Enterprise.EnterpriseId),
				"text" : elementAttribute.Element.ElementTemplate.Site.Enterprise.Name},
			{"url" : url_for("elements.selectElement", selectedClass = "Site",
				selectedId = elementAttribute.Element.ElementTemplate.Site.SiteId), "text" : elementAttribute.Element.ElementTemplate.Site.Name},
			{"url" : url_for("elements.selectElement", selectedClass = "ElementTemplate",
				selectedId = elementAttribute.Element.ElementTemplate.ElementTemplateId), "text" : elementAttribute.Element.ElementTemplate.Name},
			{"url" : url_for("elements.dashboard", elementId = elementAttribute.Element.ElementId), "text" : elementAttribute.Element.Name},
			{"url" : url_for("tagValues.listTagValues", tagId = tag.TagId, elementAttributeId = elementAttribute.ElementAttributeId),
				"text" : elementAttribute.ElementAttributeTemplate.Name}]
	elif eventFrameId:
		eventFrame = EventFrame.query.get_or_404(eventFrameId)
		breadcrumbs = [{"url" : url_for("tags.selectTag", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Enterprise",
				selectedId = eventFrame.Element.ElementTemplate.Site.Enterprise.EnterpriseId),
				"text" : eventFrame.Element.ElementTemplate.Site.Enterprise.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Site", selectedId = eventFrame.Element.ElementTemplate.Site.SiteId),
				"text" : eventFrame.Element.ElementTemplate.Site.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "ElementTemplate",
				selectedId = eventFrame.Element.ElementTemplate.ElementTemplateId), "text" : eventFrame.Element.ElementTemplate.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "EventFrameTemplate",
				selectedId = eventFrame.EventFrameTemplate.EventFrameTemplateId), "text" : eventFrame.EventFrameTemplate.Name},
			{"url" : url_for("eventFrames.dashboard", eventFrameId = eventFrame.EventFrameId), "text" : eventFrame.Name},
			{"url" : url_for("tagValues.listTagValues", eventFrameId = eventFrame.EventFrameId, eventFrameAttributeId = eventFrameAttributeId), 
				"text" : eventFrameAttribute.EventFrameAttributeTemplate.Name}]
	else:
		breadcrumbs = [{"url" : url_for("tags.selectTag", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
			{"url" : url_for("tags.selectTag", selectedClass = "Enterprise", selectedId = tag.Area.Site.Enterprise.EnterpriseId),
				"text" : tag.Area.Site.Enterprise.Name},
			{"url" : url_for("tags.selectTag", selectedClass = "Site", selectedId = tag.Area.Site.SiteId), "text" : tag.Area.Site.Name},
			{"url" : url_for("tags.selectTag", selectedClass = "Area", selectedId = tag.Area.AreaId), "text" : tag.Area.Name},
			{"url" : url_for("tagValues.listTagValues", tagId = tag.TagId), "text" : tag.Name}]

	return render_template("addEditWithTimestamp.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@tagValues.route("/tagValues/delete/<int:tagValueId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def deleteTagValue(tagValueId):
	tagValue = TagValue.query.get_or_404(tagValueId)
	tagValue.delete()
	db.session.commit()
	flash("You have successfully deleted the tag value.", "alert alert-success")
	return redirect(request.referrer)

@tagValues.route("/tagValues/edit/<int:tagValueId>", methods = ["GET", "POST"])
@tagValues.route("/tagValues/edit/<int:tagValueId>/<int:elementAttributeId>", methods = ["GET", "POST"])
@tagValues.route("/tagValues/edit/<int:tagValueId>/<int:eventFrameId>/<int:eventFrameAttributeId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def editTagValue(tagValueId, elementAttributeId = None, eventFrameId = None, eventFrameAttributeId = None):
	operation = "Edit"
	tagValue = TagValue.query.get_or_404(tagValueId)
	tag = Tag.query.get_or_404(tagValue.TagId)
	form = TagValueForm(obj = tagValue)

	# Configure the form based on if the tag value is associated with a lookup.
	if tag.LookupId:
		form.lookupValue.choices = [(lookupValue.Value, lookupValue.Name) for lookupValue in LookupValue.query. \
			filter(LookupValue.LookupId == tag.LookupId, or_(LookupValue.Selectable == True, LookupValue.Value == tagValue.Value))]
		del form.value
	else:
		del form.lookupValue

	# Edit an existing tagValue.
	if form.validate_on_submit():
		tagValue.TagId = form.tagId.data
		tagValue.Timestamp = form.utcTimestamp.data
		tagValue.UserId = current_user.get_id()

		if tag.LookupId:
			tagValue.Value = form.lookupValue.data
		else:
			tagValue.Value = form.value.data

		db.session.commit()
		flash("You have successfully edited the tag value.", "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to edit an existing tagValue.
	form.tagValueId.data = tagValue.TagValueId
	form.tagId.data = tagValue.TagId
	form.timestamp.data = tagValue.Timestamp
	if tag.LookupId:
		form.lookupValue.data = tagValue.Value
	else:
		form.value.data = tagValue.Value

	if form.requestReferrer.data is None:
		form.requestReferrer.data = request.referrer

	if elementAttributeId:
		elementAttribute = ElementAttribute.query.get_or_404(elementAttributeId)
		breadcrumbs = [{"url" : url_for("tags.selectTag", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
			{"url" : url_for("elements.selectElement", selectedClass = "Enterprise",
				selectedId = elementAttribute.Element.ElementTemplate.Site.Enterprise.EnterpriseId),
				"text" : elementAttribute.Element.ElementTemplate.Site.Enterprise.Name},
			{"url" : url_for("elements.selectElement", selectedClass = "Site",
				selectedId = elementAttribute.Element.ElementTemplate.Site.SiteId), "text" : elementAttribute.Element.ElementTemplate.Site.Name},
			{"url" : url_for("elements.selectElement", selectedClass = "ElementTemplate",
				selectedId = elementAttribute.Element.ElementTemplate.ElementTemplateId), "text" : elementAttribute.Element.ElementTemplate.Name},
			{"url" : url_for("elements.dashboard", elementId = elementAttribute.Element.ElementId), "text" : elementAttribute.Element.Name},
			{"url" : url_for("tagValues.listTagValues", elementAttributeId = elementAttribute.ElementAttributeId),
				"text" : elementAttribute.ElementAttributeTemplate.Name},
			{"url" : None, "text" : tagValue.Timestamp, "type" : "timestamp"}]
	elif eventFrameId:
		eventFrame = EventFrame.query.get_or_404(eventFrameId)
		eventFrameAttribute = EventFrameAttribute.query.get_or_404(eventFrameAttributeId)
		breadcrumbs = [{"url" : url_for("tags.selectTag", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Enterprise",
				selectedId = eventFrame.Element.ElementTemplate.Site.Enterprise.EnterpriseId),
				"text" : eventFrame.Element.ElementTemplate.Site.Enterprise.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Site", selectedId = eventFrame.Element.ElementTemplate.Site.SiteId),
				"text" : eventFrame.Element.ElementTemplate.Site.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "ElementTemplate",
				selectedId = eventFrame.Element.ElementTemplate.ElementTemplateId), "text" : eventFrame.Element.ElementTemplate.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "EventFrameTemplate",
				selectedId = eventFrame.EventFrameTemplate.EventFrameTemplateId), "text" : eventFrame.EventFrameTemplate.Name},
			{"url" : url_for("eventFrames.dashboard", eventFrameId = eventFrame.EventFrameId), "text" : eventFrame.Name},
			{"url" : url_for("tagValues.listTagValues", eventFrameId = eventFrame.EventFrameId,
				eventFrameAttributeId = eventFrameAttribute.EventFrameAttributeId), "text" : eventFrameAttribute.EventFrameAttributeTemplate.Name},
			{"url" : None, "text" : tagValue.Timestamp}]
	else:
		breadcrumbs = [{"url" : url_for("tags.selectTag", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
			{"url" : url_for("tags.selectTag", selectedClass = "Enterprise", selectedId = tag.Area.Site.Enterprise.EnterpriseId),
				"text" : tag.Area.Site.Enterprise.Name},
			{"url" : url_for("tags.selectTag", selectedClass = "Site", selectedId = tag.Area.Site.SiteId), "text" : tag.Area.Site.Name},
			{"url" : url_for("tags.selectTag", selectedClass = "Area", selectedId = tag.Area.AreaId), "text" : tag.Area.Name},
			{"url" : url_for("tagValues.listTagValues", tagId = tag.TagId), "text" : tag.Name},
			{"url" : None, "text" : tagValue.Timestamp, "type" : "timestamp"}]

	return render_template("addEditWithTimestamp.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)
