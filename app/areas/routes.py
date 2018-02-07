from flask import flash, redirect, render_template, request, url_for
from sqlalchemy import text
from . import areas
from . forms import AreaForm
from .. import db
from .. models import Area, Enterprise, Site

modelName = "Area"

@areas.route("/areas", methods = ["GET", "POST"])
@areas.route("/areas/<string:sortColumn>", methods = ["GET", "POST"])
# @login_required
def listAreas(sortColumn = ""):
	# check_admin()
	if sortColumn != "":
		sortColumn = sortColumn + ", "
	areas = Area.query.join(Site, Enterprise).order_by(text(sortColumn + "Enterprise.Abbreviation, Site.Abbreviation, Area.Name"))
	return render_template("areas/areas.html", areas = areas)

@areas.route("/areas/add", methods = ["GET", "POST"])
# @login_required
def addArea():
	# check_admin()
	operation = "Add"
	form = AreaForm()

	# Add a new area.
	if form.validate_on_submit():
		area = Area(Abbreviation = form.abbreviation.data, Description = form.description.data, Name = form.name.data, Site = form.site.data)
		db.session.add(area)
		db.session.commit()
		flash("You have successfully added the new area \"" + area.Name + "\".")
		return redirect(url_for("areas.listAreas"))

	# Present a form to add a new area.
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@areas.route("/areas/delete/<int:areaId>", methods = ["GET", "POST"])
# @login_required
def deleteArea(areaId):
	# check_admin()
	area = Area.query.get_or_404(areaId)
	db.session.delete(area)
	db.session.commit()
	flash("You have successfully deleted the area \"" + area.Name + "\".")
	return redirect(url_for("areas.listAreas"))

@areas.route("/areas/edit/<int:areaId>", methods = ["GET", "POST"])
# @login_required
def editArea(areaId):
	# check_admin()
	operation = "Edit"
	area = Area.query.get_or_404(areaId)
	form = AreaForm(obj = area)

	# Edit an existing area.
	if form.validate_on_submit():
		area.Abbreviation = form.abbreviation.data
		area.Description = form.description.data
		area.Name = form.name.data
		area.Site = form.site.data
		db.session.commit()
		flash("You have successfully edited the area \"" + area.Name + "\".")
		return redirect(url_for("areas.listAreas"))

	# Present a form to edit an existing area.
	form.abbreviation.data = area.Abbreviation
	form.description.data = area.Description
	form.name.data = area.Name
	form.site.data = area.Site
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)
