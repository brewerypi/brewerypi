from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import or_
from . import tagValues
from . forms import TagValueForm
from .. import db
from .. decorators import permissionRequired
from .. models import Area, ElementAttribute, Enterprise, Lookup, LookupValue, Permission, Site, Tag, TagValue

modelName = "Tag Value"

@tagValues.route("/tagValues/<int:tagId>", methods = ["GET", "POST"])
@tagValues.route("/tagValues/<int:tagId>/<int:elementAttributeId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def listTagValues(tagId, elementAttributeId = None):
	if elementAttributeId:
		elementAttribute = ElementAttribute.query.get_or_404(elementAttributeId)
	else:
		elementAttribute = None

	tag = Tag.query.get_or_404(tagId)
	if tag.LookupId:
		tagValues = TagValue.query.join(Tag, Lookup, LookupValue).filter(Tag.TagId == tagId, TagValue.Value == LookupValue.Value)
	else:
		tagValues = TagValue.query.filter_by(TagId = tagId)
	return render_template("tagValues/tagValues.html", elementAttribute = elementAttribute, tag = tag, tagValues = tagValues)

@tagValues.route("/tagValues/addMultiple", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def addMultiple():
	# Get the data, loop through it and add new value.
	data = request.get_json(force = True)
	count = 0
	for item in data:
		tagValue = TagValue(TagId = item["tagId"], Timestamp = item["timestamp"], Value = item["value"])
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
@tagValues.route("/tagValues/add/<int:tagId>/<int:elementAttributeId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def addTagValue(tagId, elementAttributeId = None):
	operation = "Add"
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
			tagValue = TagValue(TagId = form.tagId.data, Timestamp = form.timestamp.data, Value = form.lookupValue.data)
		else:
			tagValue = TagValue(TagId = form.tagId.data, Timestamp = form.timestamp.data, Value = form.value.data)

		db.session.add(tagValue)
		db.session.commit()
		flash("You have successfully added a new tag value.", "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to add a new tag value.
	form.tagId.data = tagId
	form.requestReferrer.data = request.referrer
	if elementAttributeId:
		elementAttribute = ElementAttribute.query.get_or_404(elementAttributeId)
		breadcrumbs = [{"url" : url_for("tags.selectTag", selectedClass = "Root"), "text" : ".."},
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
	else:
		breadcrumbs = [{"url" : url_for("tags.selectTag", selectedClass = "Root"), "text" : ".."},
			{"url" : url_for("tags.selectTag", selectedClass = "Enterprise", selectedId = tag.Area.Site.Enterprise.EnterpriseId),
				"text" : tag.Area.Site.Enterprise.Name},
			{"url" : url_for("tags.selectTag", selectedClass = "Site", selectedId = tag.Area.Site.SiteId), "text" : tag.Area.Site.Name},
			{"url" : url_for("tags.selectTag", selectedClass = "Area", selectedId = tag.Area.AreaId), "text" : tag.Area.Name},
			{"url" : url_for("tagValues.listTagValues", tagId = tag.TagId), "text" : tag.Name}]

	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@tagValues.route("/tagValues/delete/<int:tagValueId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def deleteTagValue(tagValueId):
	tagValue = TagValue.query.get_or_404(tagValueId)
	db.session.delete(tagValue)
	db.session.commit()
	flash("You have successfully deleted the tag value.", "alert alert-success")
	return redirect(request.referrer)

@tagValues.route("/tagValues/edit/<int:tagValueId>", methods = ["GET", "POST"])
@tagValues.route("/tagValues/edit/<int:tagValueId>/<int:elementAttributeId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def editTagValue(tagValueId, elementAttributeId = None):
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
		tagValue.Timestamp = form.timestamp.data

		if tag.LookupId:
			tagValue.Value = form.lookupValue.data
		else:
			tagValue.Value = form.value.data

		db.session.commit()
		flash("You have successfully edited the tag value.", "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to edit an existing tagValue.
	form.tagId.data = tagValue.TagId
	form.timestamp.data = tagValue.Timestamp

	if tag.LookupId:
		form.lookupValue.data = tagValue.Value
	else:
		form.value.data = tagValue.Value

	form.requestReferrer.data = request.referrer
	if elementAttributeId:
		elementAttribute = ElementAttribute.query.get_or_404(elementAttributeId)
		breadcrumbs = [{"url" : url_for("tags.selectTag", selectedClass = "Root"), "text" : ".."},
			{"url" : url_for("elements.selectElement", selectedClass = "Enterprise",
				selectedId = elementAttribute.Element.ElementTemplate.Site.Enterprise.EnterpriseId),
				"text" : elementAttribute.Element.ElementTemplate.Site.Enterprise.Name},
			{"url" : url_for("elements.selectElement", selectedClass = "Site",
				selectedId = elementAttribute.Element.ElementTemplate.Site.SiteId), "text" : elementAttribute.Element.ElementTemplate.Site.Name},
			{"url" : url_for("elements.selectElement", selectedClass = "ElementTemplate",
				selectedId = elementAttribute.Element.ElementTemplate.ElementTemplateId), "text" : elementAttribute.Element.ElementTemplate.Name},
			{"url" : url_for("elements.dashboard", elementId = elementAttribute.Element.ElementId), "text" : elementAttribute.Element.Name},
			{"url" : None, "text" : elementAttribute.ElementAttributeTemplate.Name},
			{"url" : None, "text" : tagValue.Timestamp}]
	else:
		breadcrumbs = [{"url" : url_for("tags.selectTag", selectedClass = "Root"), "text" : ".."},
			{"url" : url_for("tags.selectTag", selectedClass = "Enterprise", selectedId = tag.Area.Site.Enterprise.EnterpriseId),
				"text" : tag.Area.Site.Enterprise.Name},
			{"url" : url_for("tags.selectTag", selectedClass = "Site", selectedId = tag.Area.Site.SiteId), "text" : tag.Area.Site.Name},
			{"url" : url_for("tags.selectTag", selectedClass = "Area", selectedId = tag.Area.AreaId), "text" : tag.Area.Name},
			{"url" : url_for("tagValues.listTagValues", tagId = tag.TagId), "text" : tag.Name},
			{"url" : None, "text" : tagValue.Timestamp}]

	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)
