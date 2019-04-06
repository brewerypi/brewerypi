import csv
import os
from flask import current_app, flash, redirect, render_template, request, send_file, url_for
from flask_login import login_required
from . import tags
from . forms import TagForm, TagImportForm
from .. import db
from .. decorators import adminRequired, permissionRequired
from .. models import Area, Enterprise, Lookup, Permission, Site, Tag, UnitOfMeasurement

@tags.route("/tags/add/<int:areaId>", methods = ["GET", "POST"])
@tags.route("/tags/add/<int:areaId>/<int:lookup>", methods = ["GET", "POST"])
@login_required
@adminRequired
def addTag(areaId, lookup = False):
	operation = "Add"
	form = TagForm()

	area = Area.query.get_or_404(areaId)
	if lookup:
		modelName = "Lookup Tag"
		del form.unitOfMeasurement
		form.lookup.choices = [(lookup.LookupId, lookup.Name) for lookup in Lookup.query. \
			filter_by(EnterpriseId = area.Site.Enterprise.EnterpriseId).order_by(Lookup.Name)]
	else:
		modelName = "Tag"
		del form.lookup

	# Add a new tag.
	if form.validate_on_submit():
		if lookup:
			tag = Tag(AreaId = form.areaId.data, Description = form.description.data, LookupId = form.lookup.data, Name = form.name.data)
		else:
			tag = Tag(AreaId = form.areaId.data, Description = form.description.data, Name = form.name.data, UnitOfMeasurement = form.unitOfMeasurement.data)

		db.session.add(tag)
		db.session.commit()
		flash("You have successfully added the new tag \"{}\".".format(tag.Name), "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to add a new tag.
	form.areaId.data = areaId
	if form.requestReferrer.data is None:
		form.requestReferrer.data = request.referrer

	breadcrumbs = [{"url" : url_for("tags.selectTag", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
		{"url" : url_for("tags.selectTag", selectedClass = "Enterprise", selectedId = area.Site.Enterprise.EnterpriseId), "text" : area.Site.Enterprise.Name},
		{"url" : url_for("tags.selectTag", selectedClass = "Site", selectedId = area.Site.SiteId), "text" : area.Site.Name},
		{"url" : url_for("tags.selectTag", selectedClass = "Area", selectedId = area.AreaId), "text" : area.Name}]
	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@tags.route("/tags/delete/<int:tagId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def deleteTag(tagId):
	tag = Tag.query.get_or_404(tagId)
	tag.delete()
	db.session.commit()
	flash("You have successfully deleted the tag \"{}\".".format(tag.Name), "alert alert-success")
	return redirect(request.referrer)

@tags.route("/tags/edit/<int:tagId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def editTag(tagId):
	operation = "Edit"
	tag = Tag.query.get_or_404(tagId)
	form = TagForm(obj = tag)

	if tag.LookupId:
		modelName = "Lookup Tag"
		del form.unitOfMeasurement
		form.lookup.choices = [(lookup.LookupId, lookup.Name) for lookup in Lookup.query. \
			filter_by(EnterpriseId = tag.Area.Site.Enterprise.EnterpriseId).order_by(Lookup.Name)]
	else:
		modelName = "Tag"
		del form.lookup

	# Edit an existing tag.
	if form.validate_on_submit():
		tag.AreaId = form.areaId.data
		tag.Description = form.description.data
		tag.Name = form.name.data

		if tag.LookupId:
			tag.LookupId = form.lookup.data
		else:
			tag.UnitOfMeasurement = form.unitOfMeasurement.data

		db.session.commit()
		flash("You have successfully edited the tag \"{}\".".format(tag.Name), "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to edit an existing tag.
	form.tagId.data = tag.TagId
	form.areaId.data = tag.AreaId
	form.description.data = tag.Description
	form.name.data = tag.Name
	if tag.LookupId:
		form.lookup.data = tag.LookupId
	else:
		form.unitOfMeasurement.data = tag.UnitOfMeasurement

	if form.requestReferrer.data is None:
		form.requestReferrer.data = request.referrer

	breadcrumbs = [{"url" : url_for("tags.selectTag", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
		{"url" : url_for("tags.selectTag", selectedClass = "Enterprise", selectedId = tag.Area.Site.Enterprise.EnterpriseId),
			"text" : tag.Area.Site.Enterprise.Name},
		{"url" : url_for("tags.selectTag", selectedClass = "Site", selectedId = tag.Area.Site.SiteId), "text" : tag.Area.Site.Name},
		{"url" : url_for("tags.selectTag", selectedClass = "Area", selectedId = tag.Area.AreaId), "text" : tag.Area.Name},
		{"url" : None, "text" : tag.Name}]
	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@tags.route("/tags/export")
@login_required
@adminRequired
def exportTags():
	tags = Tag.query.outerjoin(Lookup).join(Area, Site, Enterprise).order_by(Enterprise.Abbreviation, Site.Abbreviation, Area.Abbreviation, Tag.Name)
	with open(os.path.join(current_app.config["EXPORT_FOLDER"], current_app.config["EXPORT_TAGS_FILENAME"]), "w", encoding = "latin-1") as tagsFile:
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
@login_required
@adminRequired
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
		with open(os.path.join(current_app.config["IMPORT_FOLDER"], current_app.config["IMPORT_TAGS_FILENAME"]), "r", encoding = "latin-1") as tagsFile:
			tagsReader = csv.DictReader(tagsFile, delimiter = ",")

			# Make sure that the header is well formed.
			if "Selected" not in tagsReader.fieldnames or "Tag Id" not in tagsReader.fieldnames or "Enterprise" not in tagsReader.fieldnames or \
				"Site" not in tagsReader.fieldnames or "Area" not in tagsReader.fieldnames or "Tag Name" not in tagsReader.fieldnames or \
				"Tag Description" not in tagsReader.fieldnames or "Lookup" not in tagsReader.fieldnames or "Unit" not in tagsReader.fieldnames:
				errors.append("Header malformed. Aborting upload.")
			else:
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

					area = Area.query.filter(Area.Abbreviation == areaAbbreviation, Area.SiteId == site.SiteId).first()
					if area is None:
						errors.append("Area \"{}\" does not exist. Skipping row {}.".format(areaAbbreviation, str(rowNumber)))
						continue

					lookup = Lookup.query.filter(Lookup.EnterpriseId == enterprise.EnterpriseId, Lookup.Name == lookupName).first()
					unit = UnitOfMeasurement.query.filter(UnitOfMeasurement.Abbreviation == UnitOfMeasurementAbbreviation).first()
					if lookup is None and unit is None:
						errors.append("Lookup and Unit can't be found. Skipping row {}.".format(str(rowNumber)))
						continue

					if "" == tagId:
						# Add tag.
						# Check for existing tag.
						tag = Tag.query.join(Area).filter(Tag.AreaId == area.AreaId, Tag.Name == tagName).first()
						if tag is not None:
							warnings.append("Tag \"{}\" already exists. Skipping row {}.".format(tagName, str(rowNumber)))
							continue
						
						if lookup:
							tag = Tag(Area = area, Description = tagDescription, Lookup = lookup, Name = tagName)
						else:
							tag = Tag(Area = area, Description = tagDescription, Name = tagName, UnitOfMeasurement = unit)
							
						db.session.add(tag)
						db.session.commit()
						successes.append("Tag \"{}\" added.".format(tagName))
					else:
						# Edit tag.
						tag = Tag.query.get_or_404(tagId)
						oldTagName = tag.Name

						# The area and/or tag name have changed. Check for existing tag.
						if tag.AreaId != area.AreaId or tag.Name != tagName:
							tagCheck = Tag.query.join(Area).filter(Tag.AreaId == area.AreaId, Tag.Name == tagName).first()
							if tagCheck is not None:
								warnings.append("Tag \"{}\" already exists. Skipping row {}.".format(tagName, str(rowNumber)))
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
						successes.append("Tag \"{}\" edited.".format(oldTagName))

	return render_template("import.html", errors = errors, form = form, importing = "Tags", successes = successes, warnings = warnings)

@tags.route("/tags/select", methods = ["GET", "POST"]) # Default.
@tags.route("/tags/select/<string:selectedClass>", methods = ["GET", "POST"]) # Root.
@tags.route("/tags/select/<string:selectedClass>/<int:selectedId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def selectTag(selectedClass = None, selectedId = None):
	if selectedClass == None:
		parent = Site.query.join(Enterprise).order_by(Enterprise.Name, Site.Name).first()
		if parent is None:
			flash("You must create a Site first.", "alert alert-danger")
			return redirect(request.referrer)
		else:
			children = Area.query.filter_by(SiteId = parent.id())
			childrenClass = "Area"
	elif selectedClass == "Root":
		parent = None
		children = Enterprise.query.order_by(Enterprise.Name)
		childrenClass = "Enterprise"
	elif selectedClass == "Enterprise":
		parent = Enterprise.query.get_or_404(selectedId)
		children = Site.query.filter_by(EnterpriseId = selectedId)
		childrenClass = "Site"
	elif selectedClass == "Site":
		parent = Site.query.get_or_404(selectedId)
		children = Area.query.filter_by(SiteId = selectedId)
		childrenClass = "Area"
	elif selectedClass == "Area":
		parent = Area.query.get_or_404(selectedId)
		children = Tag.query.filter_by(AreaId = selectedId)
		childrenClass = "Tag"

	return render_template("tags/select.html", children = children, childrenClass = childrenClass, parent = parent)
