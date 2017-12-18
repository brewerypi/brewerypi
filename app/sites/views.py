from flask import flash, redirect, render_template, request, url_for
from . import sites
from . forms import SiteForm
from .. import db
from .. models import Enterprise, Site

modelName = "Site"

@sites.route("/sites", methods = ["GET", "POST"])
# @login_required
def listSites():
	# check_admin()
	sites = Site.query.join(Enterprise).order_by(Enterprise.Name, Site.Name)
	return render_template("sites/sites.html", sites = sites)

@sites.route("/sites/add", methods = ["GET", "POST"])
# @login_required
def addSite():
	# check_admin()
	operation = "Add"
	form = SiteForm()

	# Add a new site.
	if form.validate_on_submit():
		site = Site(Abbreviation = form.abbreviation.data, Description = form.description.data, Enterprise = form.enterprise.data, Name = form.name.data)
		db.session.add(site)
		db.session.commit()
		flash("You have successfully added the new site \"" + site.Name + "\".")
		return redirect(url_for("sites.listSites"))

	# Present a form to add a new site.
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@sites.route("/sites/delete/<int:siteId>", methods = ["GET", "POST"])
# @login_required
def deleteSite(siteId):
	# check_admin()
	site = Site.query.get_or_404(siteId)
	db.session.delete(site)
	db.session.commit()
	flash("You have successfully deleted the site \"" + site.Name + "\".")
	return redirect(url_for("sites.listSites"))

@sites.route("/sites/edit/<int:siteId>", methods = ["GET", "POST"])
# @login_required
def editSite(siteId):
	# check_admin()
	operation = "Edit"
	site = Site.query.get_or_404(siteId)
	form = SiteForm(obj = site)

	# Edit an existing site.
	if form.validate_on_submit():
		site.Abbreviation = form.abbreviation.data
		site.Description = form.description.data
		site.Enterprise = form.enterprise.data
		site.Name = form.name.data
		db.session.commit()
		flash("You have successfully edited the site \"" + site.Name + "\".")
		return redirect(url_for("sites.listSites"))

	# Present a form to edit an existing site.
	form.abbreviation.data = site.Abbreviation
	form.description.data = site.Description
	form.enterprise.data = site.Enterprise
	form.name.data = site.Name
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)
