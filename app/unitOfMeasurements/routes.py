from flask import flash, redirect, render_template, request, url_for
from . import unitOfMeasurements
from . forms import UnitOfMeasurementForm
from .. import db
from .. decorators import adminRequired
from .. models import UnitOfMeasurement

modelName = "Unit"

@unitOfMeasurements.route("/unitOfMeasurements", methods = ["GET", "POST"])
@adminRequired
def listUnitOfMeasurements():
	unitOfMeasurements = UnitOfMeasurement.query
	return render_template("unitOfMeasurements/unitOfMeasurements.html", unitOfMeasurements = unitOfMeasurements)

@unitOfMeasurements.route("/units/add", methods = ["GET", "POST"])
@adminRequired
def addUnitOfMeasurement():
	operation = "Add"
	form = UnitOfMeasurementForm()

	# Add a new unit of measurement.
	if form.validate_on_submit():
		unitOfMeasurement = UnitOfMeasurement(Abbreviation = form.abbreviation.data, Name = form.name.data)
		db.session.add(unitOfMeasurement)
		db.session.commit()
		flash("You have successfully added the new unit of measurement \"" + unitOfMeasurement.Abbreviation + "\".", "alert alert-success")

		return redirect(url_for("unitOfMeasurements.listUnitOfMeasurements"))

	# Present a form to add a new unit of measurement.
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@unitOfMeasurements.route("/unitOfMeasurements/delete/<int:unitOfMeasurementId>", methods = ["GET", "POST"])
@adminRequired
def deleteUnitOfMeasurement(unitOfMeasurementId):
	unitOfMeasurement = UnitOfMeasurement.query.get_or_404(unitOfMeasurementId)
	db.session.delete(unitOfMeasurement)
	db.session.commit()
	flash("You have successfully deleted the unit of measurement \"" + unitOfMeasurement.Abbreviation + "\".", "alert alert-success")

	return redirect(url_for("unitOfMeasurements.listUnitOfMeasurements"))

@unitOfMeasurements.route("/unitOfMeasurements/edit/<int:unitOfMeasurementId>", methods = ["GET", "POST"])
@adminRequired
def editUnitOfMeasurement(unitOfMeasurementId):
	operation = "Edit"
	unitOfMeasurement = UnitOfMeasurement.query.get_or_404(unitOfMeasurementId)
	form = UnitOfMeasurementForm(obj = unitOfMeasurement)

	# Edit an existing unit of measurement.
	if form.validate_on_submit():
		unitOfMeasurement.Abbreviation = form.abbreviation.data
		unitOfMeasurement.Name = form.name.data

		db.session.commit()

		flash("You have successfully edited the unit of measurement \"" + unitOfMeasurement.Abbreviation + "\".", "alert alert-success")

		return redirect(url_for("unitOfMeasurements.listUnitOfMeasurements"))

	# Present a form to edit an existing unit of measurement.
	form.abbreviation.data = unitOfMeasurement.Abbreviation
	form.name.data = unitOfMeasurement.Name
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)
