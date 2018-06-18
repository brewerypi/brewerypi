from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import and_
from . import unitOfMeasurements
from . forms import UnitOfMeasurementForm
from .. import db
from .. decorators import adminRequired
from .. models import UnitOfMeasurement

modelName = "Unit"

@unitOfMeasurements.route("/unitOfMeasurements", methods = ["GET", "POST"])
@login_required
@adminRequired
def listUnitOfMeasurements():
	unitOfMeasurements = UnitOfMeasurement.query
	return render_template("unitOfMeasurements/unitOfMeasurements.html", unitOfMeasurements = unitOfMeasurements)

@unitOfMeasurements.route("/units/add", methods = ["GET", "POST"])
@login_required
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

@unitOfMeasurements.route("/units/addDefaultUnitsOfMeasurements", methods = ["GET", "POST"])
@login_required
@adminRequired
def addDefaultUnitsOfMeasurements():
	defaultUnits = {"°C" : "degree Celsius",
		"°F" : "degree Fahrenheit",
		"°F/min" : "degree Fahrenheit per minute",
		"ASBC" : "American Society of Brewing Chemists",
		"bbl" : "barrel",
		"cells/ml" : "cells per milliliter",
		"cells/ml/°P" : "cells per ml per degree plato",
		"EBC" : "european brewery convention",
		"g" : "grams",
		"g/bbl" : "grams per barrel",
		"g/L" : "grams per liter",
		"gal" : "gallon",
		"gpm" : "gallons per minute",
		"h" : "hour",
		"IBU" : "international bittering unit",
		"in" : "inches",
		"kg" : "kilogram",
		"L" : "Liters",
		"lb" : "pound",
		"lb/bbl" : "pounds / barrel",
		"mg" : "milligram",
		"min" : "minute",
		"mL" : "milliliter",
		"mm" : "millimeter",
		"pH" : "potential of hydrogen",
		"ppb" : "parts per billion",
		"ppm" : "parts per million",
		"psi" : "pounds per square inch",
		"RE" : "real extract",
		"s" : "second",
		"SG" : "specific gravity",
		"SRM" : "Standard Reference Method",
		"t/h" : "tons per hour",
		"TA" : "Total Acidity",
		"vol" : "volumes",
		"x10^12 cells" : "x10^12 cells",
		"x10^6 cells" : "x10^6 cells"}			
			
	added = []
	flash("Inserting default units of measurements if needed...", "alert alert-warning")
	for defaultUnit in defaultUnits:
		unit = UnitOfMeasurement.query.filter(and_(UnitOfMeasurement.Abbreviation == defaultUnit,
			UnitOfMeasurement.Name == defaultUnits[defaultUnit])).first()
		added = defaultUnit
		if unit is None:
			# flash("Adding unit \"{}\".".format(defaultUnit), "alert alert-success")
			unit = UnitOfMeasurement(Abbreviation = defaultUnit)
			unit.Name = defaultUnits[defaultUnit]
			db.session.add(unit)
	db.session.commit()
	
	addedMessage = None
	if added:
		for unit in added:
			if addedMessage == None:
				addedMessage = "Added: {}".format(unit)
			else:
				addedMessage = "{}, {}".format(addedMessage, unit)
		"{}.".format(addedMessage)
	else:
		addedMessage = "Added: none."
	flash(addedMessage)

	return redirect(url_for("unitOfMeasurements.listUnitOfMeasurements"))

@unitOfMeasurements.route("/unitOfMeasurements/delete/<int:unitOfMeasurementId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def deleteUnitOfMeasurement(unitOfMeasurementId):
	unitOfMeasurement = UnitOfMeasurement.query.get_or_404(unitOfMeasurementId)
	db.session.delete(unitOfMeasurement)
	db.session.commit()
	flash("You have successfully deleted the unit of measurement \"" + unitOfMeasurement.Abbreviation + "\".", "alert alert-success")

	return redirect(url_for("unitOfMeasurements.listUnitOfMeasurements"))

@unitOfMeasurements.route("/unitOfMeasurements/edit/<int:unitOfMeasurementId>", methods = ["GET", "POST"])
@login_required
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
