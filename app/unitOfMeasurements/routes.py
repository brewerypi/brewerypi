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
		flash("You have successfully added the new unit of measurement \"{}\".".format(unitOfMeasurement.Abbreviation), "alert alert-success")

		return redirect(url_for("unitOfMeasurements.listUnitOfMeasurements"))

	# Present a form to add a new unit of measurement.
	breadcrumbs = [{"url" : url_for("unitOfMeasurements.listUnitOfMeasurements"), "text" : ".."}]
	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@unitOfMeasurements.route("/units/addDefaultUnitsOfMeasurements", methods = ["GET", "POST"])
@login_required
@adminRequired
def addDefaultUnitsOfMeasurements():
	defaultUnits = {"ASBC" : "american society of brewing chemists",
		"ADF" : "apparent degree of fermentation",
		"bbl" : "barrel",
		"cells/ml" : "cells per milliliter",
		"cells/ml/°P" : "cells per ml per degree plato",
		"°C" : "degree celsius",
		"°F" : "degree fahrenheit",
		"°F/min" : "degree fahrenheit per minute",
		"EBC" : "european brewery convention",
		"gal" : "gallon",
		"gpm" : "gallons per minute",
		"g" : "grams",
		"g/bbl" : "grams per barrel",
		"g/L" : "grams per liter",
		"h" : "hour",
		"in" : "inches",
		"IBU" : "international bittering unit",
		"kg" : "kilogram",
		"L" : "liters",
		"mg" : "milligram",
		"mL" : "milliliter",
		"mm" : "millimeter",
		"min" : "minute",
		"ppb" : "parts per billion",
		"ppm" : "parts per million",
		"%" : "percentage",
		"pH" : "potential of hydrogen",
		"lb" : "pound",
		"lb/bbl" : "pounds per barrel",
		"psi" : "pounds per square inch",
		"RDF" : "real degree of fermentation",
		"RE" : "real extract",
		"s" : "second",
		"SG" : "specific gravity",
		"SRM" : "standard reference method",
		"t/h" : "tons per hour",
		"TA" : "total acidity",
		"vol" : "volumes",
		"x10^12 cells" : "x10^12 cells",
		"x10^6 cells" : "x10^6 cells"}			
			
	addedUnits = []
	skippedUnits = []
	for defaultUnit in defaultUnits:
		unit = UnitOfMeasurement.query.filter(and_(UnitOfMeasurement.Abbreviation == defaultUnit,
			UnitOfMeasurement.Name == defaultUnits[defaultUnit])).first()
		if unit is None:
			addedUnits.append(defaultUnits[defaultUnit])
			unit = UnitOfMeasurement(Abbreviation = defaultUnit)
			unit.Name = defaultUnits[defaultUnit]
			db.session.add(unit)
		else:
			skippedUnits.append(defaultUnits[defaultUnit])
	db.session.commit()
	
	addedMessage = ""
	alert = "alert alert-warning"
	if addedUnits:
		for unit in addedUnits:
			if addedMessage == "":
				addedMessage = "Added: {}".format(unit)
				alert = "alert alert-success"
			else:
				addedMessage = "{}, {}".format(addedMessage, unit)
		addedMessage = "{}.".format(addedMessage)
	else:
		addedMessage = "Added none of the default units of measurements."
	flash(addedMessage, alert)

	skippedMessage = ""
	if skippedUnits:
		for unit in skippedUnits:
			if skippedMessage == "":
				skippedMessage = "Skipped: {}".format(unit)
			else:
				skippedMessage = "{}, {}".format(skippedMessage, unit)
		skippedMessage = "{} as they already exist.".format(skippedMessage)
		flash(skippedMessage, "alert alert-warning")

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

		flash("You have successfully edited the unit of measurement \"{}\".".format(unitOfMeasurement.Abbreviation), "alert alert-success")

		return redirect(url_for("unitOfMeasurements.listUnitOfMeasurements"))

	# Present a form to edit an existing unit of measurement.
	form.abbreviation.data = unitOfMeasurement.Abbreviation
	form.name.data = unitOfMeasurement.Name
	breadcrumbs = [{"url" : url_for("unitOfMeasurements.listUnitOfMeasurements"), "text" : ".."},
		{"url" : None, "text" : unitOfMeasurement.Name}]
	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)
