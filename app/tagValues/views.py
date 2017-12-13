from flask import flash, redirect, render_template, request, url_for

from . import tagValues

from . forms import TagValueForm

from .. import db

from .. models import Area, Enterprise, LookupValue, Site, Tag, TagValue

@tagValues.route("/tagValues/<int:tagId>", methods = ["GET", "POST"])
# @login_required
def listTagValues(tagId):
	# check_admin()

	tag = Tag.query.get_or_404(tagId)

	page = request.args.get("page", 1, type = int)
	pagination = TagValue.query.join(Tag).filter_by(TagId = tagId).join(Area, Site, Enterprise).order_by(Enterprise.Abbreviation, Site.Abbreviation, Area.Abbreviation, \
		Tag.Name, TagValue.Timestamp.desc()).paginate(page, per_page = 10, error_out = False)
	tagValues = pagination.items

	return render_template("tagValues/tagValues.html", pagination = pagination, tag = tag, tagValues = tagValues)

@tagValues.route("/tagValues/add/<int:tagId>", methods = ["GET", "POST"])
# @login_required
def addTagValue(tagId):
	# check_admin()

	operation = "Add"
	tag = Tag.query.get_or_404(tagId)
	form = TagValueForm()

	# Configure the form based on if the tag value is associated with a lookup.
	if tag.LookupId:
		form.lookupValue.choices = [(lookupValue.Value, lookupValue.Name) for lookupValue in LookupValue.query.filter_by(LookupId = tag.LookupId)]
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
		flash("You have successfully added a new tag value.")

		return redirect(url_for("tagValues.listTagValues", tagId = tag.TagId))

	# Present a form to add a new tag value.
	form.tagId.data = tagId
	return render_template("tagValues/tagValue.html", form = form, operation = operation)

@tagValues.route("/tagValues/delete/<int:tagValueId>", methods = ["GET", "POST"])
# @login_required
def deleteTagValue(tagValueId):
	# check_admin()

	tagValue = TagValue.query.get_or_404(tagValueId)
	db.session.delete(tagValue)
	db.session.commit()
	flash("You have successfully deleted the tag value.")

	return redirect(url_for("tagValues.listTagValues", tagId = tagValue.TagId))

@tagValues.route("/tagValues/edit/<int:tagValueId>", methods = ["GET", "POST"])
# @login_required
def editTagValue(tagValueId):
	# check_admin()

	operation = "Edit"
	tagValue = TagValue.query.get_or_404(tagValueId)
	tag = Tag.query.get_or_404(tagValue.TagId)
	form = TagValueForm(obj = tagValue)

	# Configure the form based on if the tag value is associated with a lookup.
	if tag.LookupId:
		form.lookupValue.choices = [(lookupValue.Value, lookupValue.Name) for lookupValue in LookupValue.query.filter_by(LookupId = tag.LookupId)]
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

		flash("You have successfully edited the tag value.")

		return redirect(url_for("tagValues.listTagValues", tagId = tagValue.TagId))

	# Present a form to edit an existing tagValue.
	form.tagId.data = tagValue.TagId
	form.timestamp.data = tagValue.Timestamp

	if tag.LookupId:
		form.lookupValue.data = tagValue.Value
	else:
		form.value.data = tagValue.Value

	return render_template("tagValues/tagValue.html", form = form, operation = operation, tagValue = tagValue)
