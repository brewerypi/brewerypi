from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from . import areas
from . forms import AreaForm
from .. import db
from .. decorators import adminRequired
from .. models import Area, Site

modelName = "Area"

@areas.route("/areas/add/<int:siteId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def addArea(siteId):
	operation = "Add"
	form = AreaForm()

	# Add a new area.
	if form.validate_on_submit():
		area = Area(Abbreviation = form.abbreviation.data, Description = form.description.data, Name = form.name.data, SiteId = siteId)
		db.session.add(area)
		db.session.commit()
		flash("You have successfully added the new area \"{}\".".format(area.Name), "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to add a new area.
	form.siteId.data = siteId
	if form.requestReferrer.data is None:
		form.requestReferrer.data = request.referrer

	site = Site.query.get_or_404(siteId)
	breadcrumbs = [{"url" : url_for("physicalModels.selectPhysicalModel", selectedClass = "Root"),
		"text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
		{"url" : url_for("physicalModels.selectPhysicalModel", selectedClass = "Enterprise", selectedId = site.Enterprise.EnterpriseId),
			"text" : site.Enterprise.Name},
		{"url" : url_for("physicalModels.selectPhysicalModel", selectedClass = "Site", selectedId = site.SiteId), "text" : site.Name}]
	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@areas.route("/areas/delete/<int:areaId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def deleteArea(areaId):
	area = Area.query.get_or_404(areaId)
	area.delete()
	db.session.commit()
	flash("You have successfully deleted the area \"{}\".".format(area.Name), "alert alert-success")
	return redirect(request.referrer)

@areas.route("/areas/edit/<int:areaId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def editArea(areaId):
	operation = "Edit"
	area = Area.query.get_or_404(areaId)
	form = AreaForm(obj = area)

	# Edit an existing area.
	if form.validate_on_submit():
		area.Abbreviation = form.abbreviation.data
		area.Description = form.description.data
		area.Name = form.name.data
		area.SiteId = form.siteId.data
		db.session.commit()
		flash("You have successfully edited the area \"{}\".".format(area.Name), "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to edit an existing area.
	form.areaId.data = area.AreaId
	form.abbreviation.data = area.Abbreviation
	form.description.data = area.Description
	form.name.data = area.Name
	form.siteId.data = area.SiteId
	if form.requestReferrer.data is None:
		form.requestReferrer.data = request.referrer

	breadcrumbs = [{"url" : url_for("physicalModels.selectPhysicalModel", selectedClass = "Root"),
		"text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
		{"url" : url_for("physicalModels.selectPhysicalModel", selectedClass = "Enterprise", selectedId = area.Site.Enterprise.EnterpriseId),
			"text" : area.Site.Enterprise.Name},
		{"url" : url_for("physicalModels.selectPhysicalModel", selectedClass = "Site", selectedId = area.Site.SiteId), "text" : area.Site.Name},
		{"url" : None, "text" : area.Name}]
	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)
