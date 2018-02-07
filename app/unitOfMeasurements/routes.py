from flask import flash, redirect, render_template, request, url_for
from sqlalchemy import text
from . import unitOfMeasurements
from . forms import UnitOfMeasurementForm
from .. import db
from .. models import UnitOfMeasurement

modelName = "Unit"

@unitOfMeasurements.route("/unitOfMeasurements", methods = ["GET", "POST"])
@unitOfMeasurements.route("/unitOfMeasurements/<string:sortColumn>", methods = ["GET", "POST"])
# @login_required
def listUnitOfMeasurements(sortColumn = ""):
	# check_admin()
	if sortColumn != "":
		sortColumn = sortColumn + ", "
	page = request.args.get("page", 1, type = int)
	pagination = UnitOfMeasurement.query.order_by(text(sortColumn + "UnitOfMeasurement.Name")).paginate(page, per_page = 10, error_out = False)
	unitOfMeasurements = pagination.items

	return render_template("unitOfMeasurements/unitOfMeasurements.html", pagination = pagination, unitOfMeasurements = unitOfMeasurements)

@unitOfMeasurements.route("/units/add", methods = ["GET", "POST"])
# @login_required
def addUnitOfMeasurement():
	# check_admin()

	operation = "Add"
	form = UnitOfMeasurementForm()

	# Add a new unit of measurement.
	if form.validate_on_submit():
		unitOfMeasurement = UnitOfMeasurement(Abbreviation = form.abbreviation.data, Name = form.name.data)
		db.session.add(unitOfMeasurement)
		db.session.commit()
		flash("You have successfully added the new unit of measurement \"" + unitOfMeasurement.Abbreviation + "\".")

		return redirect(url_for("unitOfMeasurements.listUnitOfMeasurements"))

	# Present a form to add a new unit of measurement.
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@unitOfMeasurements.route("/unitOfMeasurements/delete/<int:unitOfMeasurementId>", methods = ["GET", "POST"])
# @login_required
def deleteUnitOfMeasurement(unitOfMeasurementId):
	# check_admin()

	unitOfMeasurement = UnitOfMeasurement.query.get_or_404(unitOfMeasurementId)
	db.session.delete(unitOfMeasurement)
	db.session.commit()
	flash("You have successfully deleted the unit of measurement \"" + unitOfMeasurement.Abbreviation + "\".")

	return redirect(url_for("unitOfMeasurements.listUnitOfMeasurements"))

@unitOfMeasurements.route("/unitOfMeasurements/edit/<int:unitOfMeasurementId>", methods = ["GET", "POST"])
# @login_required
def editUnitOfMeasurement(unitOfMeasurementId):
	# check_admin()

	operation = "Edit"
	unitOfMeasurement = UnitOfMeasurement.query.get_or_404(unitOfMeasurementId)
	form = UnitOfMeasurementForm(obj = unitOfMeasurement)

	# Edit an existing unit of measurement.
	if form.validate_on_submit():
		unitOfMeasurement.Abbreviation = form.abbreviation.data
		unitOfMeasurement.Name = form.name.data

		db.session.commit()

		flash("You have successfully edited the unit of measurement \"" + unitOfMeasurement.Abbreviation + "\".")

		return redirect(url_for("unitOfMeasurements.listUnitOfMeasurements"))

	# Present a form to edit an existing unit of measurement.
	form.abbreviation.data = unitOfMeasurement.Abbreviation
	form.name.data = unitOfMeasurement.Name
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)
