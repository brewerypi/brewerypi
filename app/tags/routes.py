import csv
import os
from flask import current_app, flash, redirect, render_template, request, safe_join, url_for
from werkzeug.utils import secure_filename
from . import tags
from . forms import TagForm, TagImportForm
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

@tags.route("/tags/import", methods = ["GET", "POST"])
# @login_required
def importTags():
	form = TagImportForm()
	errors = []
	successes = []
	warnings = []

	if form.validate_on_submit():
		# Save a version of the uploaded file.
		tagsFile = form.tagsFile.data
		tagsFile.save(current_app.config["TAG_IMPORT_FILE_PATH"])
		tagsFile.close()

		# Open the uploaded file.
		with open(current_app.config["TAG_IMPORT_FILE_PATH"], "r") as tagsFile:
			tagsReader = csv.DictReader(tagsFile, delimiter = ",")

			# Make sure that the header is well formed.
			if "Enterprise" not in tagsReader.fieldnames or "Site" not in tagsReader.fieldnames or "Area" not in tagsReader.fieldnames or \
				"Tag Name" not in tagsReader.fieldnames or "Tag Description" not in tagsReader.fieldnames or "Lookup" not in tagsReader.fieldnames or \
				"Unit" not in tagsReader.fieldnames:
				errors.append("Header malformed. Aborting upload.")
				return render_template("tags/importTags.html", errors = errors, form = form)

			# Iterate through each row.
			for n, row in enumerate(tagsReader, start = 1):
				enterpriseAbbreviation = row["Enterprise"].strip()
				siteAbbreviation = row["Site"].strip()
				areaAbbreviation = row["Area"].strip()
				tagName = row["Tag Name"].strip()
				tagDescription = row["Tag Description"].strip()
				lookupName = row["Lookup"].strip()
				UnitOfMeasurementAbbreviation = row["Unit"].strip()

				enterprise = Enterprise.query.filter(Enterprise.Abbreviation == enterpriseAbbreviation).first()
				if enterprise is None:
					errors.append("Enterprise \"" + enterpriseAbbreviation + "\" does not exist. Skipping row " + str(n) + ".")
					continue

				site = Site.query.filter(Site.Abbreviation == siteAbbreviation).first()
				if site is None:
					errors.append("Site \"" + siteAbbreviation + "\" does not exist. Skipping row " + str(n) + ".")
					continue

				area = Area.query.filter(Area.Abbreviation == areaAbbreviation).first()
				if area is None:
					errors.append("Area \"" + areaAbbreviation + "\" does not exist. Skipping row " + str(n) + ".")
					continue

				tag = Tag.query.join(Area).filter(Tag.AreaId == area.AreaId, Tag.Name == tagName).first()
				if tag is not None:
					warnings.append("Tag \"" + tagName + "\" already exists. Skipping row " + str(n) + ".")
					continue
					
				lookup = Lookup.query.filter(Lookup.Name == lookupName).first()
				unit = UnitOfMeasurement.query.filter(UnitOfMeasurement.Abbreviation == UnitOfMeasurementAbbreviation).first()
				if lookup is None and unit is None:
					errors.append("Lookup and Unit are empty. Skipping row " + str(n) + ".")
					continue

				if lookup:
					tag = Tag(Area = area, Description = tagDescription, Lookup = lookup, Name = tagName)
				else:
					tag = Tag(Area = area, Description = tagDescription, Name = tagName, UnitOfMeasurement = unit)

				db.session.add(tag)
				db.session.commit()
				successes.append("Tag \"" + tagName + "\" added.")

	return render_template("tags/importTags.html", errors = errors, form = form, successes = successes, warnings = warnings)
