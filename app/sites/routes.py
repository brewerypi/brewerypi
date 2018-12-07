from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from . import sites
from . forms import SiteForm
from .. import db
from .. decorators import adminRequired
from .. models import Enterprise, Site

modelName = "Site"

@sites.route("/sites/add/<int:enterpriseId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def addSite(enterpriseId):
	operation = "Add"
	form = SiteForm()

	# Add a new site.
	if form.validate_on_submit():
		site = Site(Abbreviation = form.abbreviation.data, Description = form.description.data, EnterpriseId = enterpriseId, Name = form.name.data)
		db.session.add(site)
		db.session.commit()
		flash("You have successfully added the new site \"{}\".".format(site.Name), "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to add a new site.
	if form.requestReferrer.data is None:
		# If request.referrer is None (i.e. if accessing add/edit from a bookmark), will return to home page
		form.requestReferrer.data = request.referrer
	enterprise = Enterprise.query.get_or_404(enterpriseId)
	breadcrumbs = [{"url" : url_for("physicalModels.selectPhysicalModel", selectedClass = "Root"),
		"text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
		{"url" : url_for("physicalModels.selectPhysicalModel", selectedClass = "Enterprise", selectedId = enterprise.EnterpriseId), "text" : enterprise.Name}]
	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@sites.route("/sites/delete/<int:siteId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def deleteSite(siteId):
	site = Site.query.get_or_404(siteId)
	db.session.delete(site)
	db.session.commit()
	flash("You have successfully deleted the site \"{}\".".format(site.Name), "alert alert-success")
	return redirect(request.referrer)

@sites.route("/sites/edit/<int:siteId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def editSite(siteId):
	operation = "Edit"
	site = Site.query.get_or_404(siteId)
	form = SiteForm(obj = site)

	# Edit an existing site.
	if form.validate_on_submit():
		site.Abbreviation = form.abbreviation.data
		site.Description = form.description.data
		site.EnterpriseId = form.enterpriseId.data
		site.Name = form.name.data
		db.session.commit()
		flash("You have successfully edited the site \"{}\".".format(site.Name), "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to edit an existing site.
	form.abbreviation.data = site.Abbreviation
	form.description.data = site.Description
	form.enterpriseId.data = site.EnterpriseId
	form.name.data = site.Name
	if form.requestReferrer.data is None:
		# If request.referrer is None (i.e. if accessing add/edit from a bookmark), will return to home page
		form.requestReferrer.data = request.referrer
	breadcrumbs = [{"url" : url_for("physicalModels.selectPhysicalModel", selectedClass = "Root"),
		"text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
		{"url" : url_for("physicalModels.selectPhysicalModel", selectedClass = "Enterprise", selectedId = site.Enterprise.EnterpriseId),
			"text" : site.Enterprise.Name},
		{"url" : None, "text" : site.Name}]
	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)
