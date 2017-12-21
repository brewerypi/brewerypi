from flask import flash, redirect, render_template, request, url_for
from . import tags
from . forms import TagForm
from .. import db
from .. models import Area, Enterprise, Lookup, Site, Tag, UnitOfMeasurement

@tags.route("/tags", methods = ["GET", "POST"])
# @login_required
def listTags():
	# check_admin()
	page = request.args.get("page", 1, type = int)
	pagination = Tag.query.outerjoin(Lookup).join(Area, Site, Enterprise).order_by(Enterprise.Abbreviation, Site.Abbreviation, Area.Abbreviation, \
		Tag.Name).paginate(page, per_page = 10, error_out = False)
	tags = pagination.items
	return render_template("tags/tags.html", pagination = pagination, tags = tags)

@tags.route("/tags/add", methods = ["GET", "POST"])
@tags.route("/tags/add/<int:lookup>", methods = ["GET", "POST"])
# @login_required
def addTag(lookup = False):
	# check_admin()
	operation = "Add"
	form = TagForm()

	if lookup:
		modelName = "Lookup Tag"
		del form.unitOfMeasurement
	else:
		modelName = "Tag"
		del form.lookup

	# Add a new tag.
	if form.validate_on_submit():
		if lookup:
			tag = Tag(Area = form.area.data, Description = form.description.data, Lookup = form.lookup.data, Name = form.name.data)
		else:
			tag = Tag(Area = form.area.data, Description = form.description.data, Name = form.name.data, UnitOfMeasurement = form.unitOfMeasurement.data)

		db.session.add(tag)
		db.session.commit()
		flash("You have successfully added the new tag \"" + tag.Name + "\".")
		return redirect(url_for("tags.listTags"))

	# Present a form to add a new tag.
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@tags.route("/tags/delete/<int:tagId>", methods = ["GET", "POST"])
# @login_required
def deleteTag(tagId):
	# check_admin()
	tag = Tag.query.get_or_404(tagId)
	db.session.delete(tag)
	db.session.commit()
	flash("You have successfully deleted the tag \"" + tag.Name + "\".")
	return redirect(url_for("tags.listTags"))

@tags.route("/tags/edit/<int:tagId>", methods = ["GET", "POST"])
# @login_required
def editTag(tagId):
	# check_admin()
	operation = "Edit"
	tag = Tag.query.get_or_404(tagId)
	form = TagForm(obj = tag)

	if tag.LookupId:
		modelName = "Lookup Tag"
		del form.unitOfMeasurement
	else:
		modelName = "Tag"
		del form.lookup

	# Edit an existing tag.
	if form.validate_on_submit():
		tag.Area = form.area.data
		tag.Description = form.description.data
		tag.Name = form.name.data

		if tag.LookupId:
			tag.Lookup = form.lookup.data
		else:
			tag.UnitOfMeasurement = form.unitOfMeasurement.data

		db.session.commit()
		flash("You have successfully edited the tag \"" + tag.Name + "\".")
		return redirect(url_for("tags.listTags"))

	# Present a form to edit an existing tag.
	form.area.data = tag.Area
	form.description.data = tag.Description
	form.name.data = tag.Name

	if tag.LookupId:
		form.lookup.data = tag.Lookup
	else:
		form.unitOfMeasurement.data = tag.UnitOfMeasurement

	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)
