import csv
import os
from flask import current_app, flash, redirect, render_template, request, send_file, url_for
from sqlalchemy import text
from . import tags
from . forms import TagForm, TagImportForm
from .. import db
from .. models import Area, Enterprise, Lookup, Site, Tag, UnitOfMeasurement

@tags.route("/tags", methods = ["GET", "POST"])
@tags.route("/tags/<string:sortColumn>", methods = ["GET", "POST"])
# @login_required
def listTags(sortColumn = ""):
	# check_admin()
	if sortColumn != "":
		sortColumn = sortColumn + ", "
	page = request.args.get("page", 1, type = int)
	pagination = Tag.query.outerjoin(UnitOfMeasurement, Lookup).join(Area, Site, Enterprise).order_by(text(sortColumn + "Enterprise.Abbreviation, \
		Site.Abbreviation, Area.Abbreviation, Tag.Name")).paginate(page, per_page = 10, error_out = False)
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

@tags.route("/tags/export")
def exportTags():
	tags = Tag.query.outerjoin(Lookup).join(Area, Site, Enterprise).order_by(Enterprise.Abbreviation, Site.Abbreviation, Area.Abbreviation, Tag.Name)
	with open(os.path.join(current_app.config["EXPORT_FOLDER"], current_app.config["EXPORT_TAGS_FILENAME"]), "w") as tagsFile:
		fieldnames = ["Selected", "Tag Id", "Enterprise", "Site", "Area", "Tag Name", "Tag Description", "Lookup", "Unit"]
		tagsWriter = csv.DictWriter(tagsFile, fieldnames = fieldnames, lineterminator = "\n")
		tagsWriter.writeheader()
		
		for tag in tags:
			if tag.Lookup:
				tagsWriter.writerow({"Selected" : "", "Tag Id" : tag.TagId, "Enterprise" : tag.Area.Site.Enterprise.Abbreviation, \
				"Site" : tag.Area.Site.Abbreviation, "Area" : tag.Area.Abbreviation, "Tag Name" : tag.Name, "Tag Description" : tag.Description, \
				"Lookup" : tag.Lookup.Name, "Unit" : ""})
			else:
				tagsWriter.writerow({"Selected" : "", "Tag Id" : tag.TagId, "Enterprise" : tag.Area.Site.Enterprise.Abbreviation, \
					"Site" : tag.Area.Site.Abbreviation, "Area" : tag.Area.Abbreviation, "Tag Name" : tag.Name, "Tag Description" : tag.Description, \
					"Lookup" : "", "Unit" : tag.UnitOfMeasurement.Abbreviation})
	
	return send_file(os.path.join("..", current_app.config["EXPORT_FOLDER"], current_app.config["EXPORT_TAGS_FILENAME"]), as_attachment = True)

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
		tagsFile.save(os.path.join(current_app.config["IMPORT_FOLDER"], current_app.config["IMPORT_TAGS_FILENAME"]))
		tagsFile.close()

		# Open the uploaded file.
		with open(os.path.join(current_app.config["IMPORT_FOLDER"], current_app.config["IMPORT_TAGS_FILENAME"]), "r") as tagsFile:
			tagsReader = csv.DictReader(tagsFile, delimiter = ",")

			# Make sure that the header is well formed.
			if "Selected" not in tagsReader.fieldnames or "Tag Id" not in tagsReader.fieldnames or "Enterprise" not in tagsReader.fieldnames or \
				"Site" not in tagsReader.fieldnames or "Area" not in tagsReader.fieldnames or "Tag Name" not in tagsReader.fieldnames or \
				"Tag Description" not in tagsReader.fieldnames or "Lookup" not in tagsReader.fieldnames or "Unit" not in tagsReader.fieldnames:
				errors.append("Header malformed. Aborting upload.")
				return render_template("import.html", errors = errors, form = form, importing = "Tags")

			# Iterate through each row.
			for n, row in enumerate(tagsReader, start = 1):
				rowNumber = n + 1
				selected = row["Selected"].strip()
				tagId = row["Tag Id"].strip()
				enterpriseAbbreviation = row["Enterprise"].strip()
				enterpriseAbbreviation = row["Enterprise"].strip()
				siteAbbreviation = row["Site"].strip()
				areaAbbreviation = row["Area"].strip()
				tagName = row["Tag Name"].strip()
				tagDescription = row["Tag Description"].strip()
				lookupName = row["Lookup"].strip()
				UnitOfMeasurementAbbreviation = row["Unit"].strip()

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

				area = Area.query.filter(Area.Abbreviation == areaAbbreviation, Area.SiteId == site.SiteId).first()
				if area is None:
					errors.append("Area \"" + areaAbbreviation + "\" does not exist. Skipping row " + str(rowNumber) + ".")
					continue

				lookup = Lookup.query.filter(Lookup.EnterpriseId == enterprise.EnterpriseId, Lookup.Name == lookupName).first()
				unit = UnitOfMeasurement.query.filter(UnitOfMeasurement.Abbreviation == UnitOfMeasurementAbbreviation).first()
				if lookup is None and unit is None:
					errors.append("Lookup and Unit can't be found. Skipping row " + str(rowNumber) + ".")
					continue

				if "" == tagId:
					# Add tag.
					# Check for existing tag.
					tag = Tag.query.join(Area).filter(Tag.AreaId == area.AreaId, Tag.Name == tagName).first()
					if tag is not None:
						warnings.append("Tag \"" + tagName + "\" already exists. Skipping row " + str(rowNumber) + ".")
						continue
					
					if lookup:
						tag = Tag(Area = area, Description = tagDescription, Lookup = lookup, Name = tagName)
					else:
						tag = Tag(Area = area, Description = tagDescription, Name = tagName, UnitOfMeasurement = unit)
						
					db.session.add(tag)
					db.session.commit()
					successes.append("Tag \"" + tagName + "\" added.")
				else:
					# Edit tag.
					tag = Tag.query.get_or_404(tagId)
					oldTagName = tag.Name

					# The area and/or tag name have changed. Check for existing tag.
					if tag.AreaId != area.AreaId or tag.Name != tagName:
						tagCheck = Tag.query.join(Area).filter(Tag.AreaId == area.AreaId, Tag.Name == tagName).first()
						if tagCheck is not None:
							warnings.append("Tag \"" + tagName + "\" already exists. Skipping row " + str(rowNumber) + ".")
							continue

					tag.Area = area
					tag.Description = tagDescription
					tag.Name = tagName

					if lookup:
						tag.Lookup = lookup
						tag.UnitOfMeasurement = None
					else:
						tag.Lookup = None
						tag.UnitOfMeasurement = unit

					db.session.commit()
					successes.append("Tag \"" + oldTagName + "\" edited.")

	return render_template("import.html", errors = errors, form = form, importing = "Tags", successes = successes, warnings = warnings)
