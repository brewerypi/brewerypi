from flask import flash, redirect, render_template, request, url_for
from . import lookupValues
from . forms import LookupValueForm
from .. import db
from .. decorators import adminRequired
from .. models import Enterprise, Lookup, LookupValue

modelName = "Lookup Value"

@lookupValues.route("/lookupValues/<int:lookupId>", methods = ["GET", "POST"])
@adminRequired
def listLookupValues(lookupId):
	# check_admin()
	lookup = Lookup.query.get_or_404(lookupId)
	lookupValues = LookupValue.query.filter_by(LookupId = lookupId)
	return render_template("lookupValues/lookupValues.html", lookup = lookup, lookupValues = lookupValues)

@lookupValues.route("/lookupValues/add/<int:lookupId>", methods = ["GET", "POST"])
@adminRequired
def addLookupValue(lookupId):
	# check_admin()
	operation = "Add"
	form = LookupValueForm()

	# Determine the next lookup value.
	maximumLookupValue = LookupValue.query.filter_by(LookupId = lookupId).order_by(LookupValue.Value.desc()).first()
	if maximumLookupValue:
		form.value.data = int(maximumLookupValue.Value) + 1
	else:
		form.value.data = 0

	# Add a new lookupValue.
	if form.validate_on_submit():
		lookupValue = LookupValue(LookupId = form.lookupId.data, Name = form.name.data, Selectable = form.selectable.data, Value = form.value.data)
		db.session.add(lookupValue)
		db.session.commit()
		flash("You have successfully added the new lookup value \"" + lookupValue.Name + "\".", "alert alert-success")
		return redirect(url_for("lookupValues.listLookupValues", lookupId = lookupId))

	# Present a form to add a new lookupValue.
	form.lookupId.data = lookupId
	form.selectable.data = True
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@lookupValues.route("/lookupValues/delete/<int:lookupValueId>", methods = ["GET", "POST"])
@adminRequired
def deleteLookupValue(lookupValueId):
	# check_admin()
	lookupValue = LookupValue.query.get_or_404(lookupValueId)
	if lookupValue.isReferenced():
		flash("Lookup value \"" + lookupValue.Name + "\" is referenced by one or more tag values and cannot be deleted.", "alert alert-danger")
	else:
		db.session.delete(lookupValue)
		db.session.commit()
		flash("You have successfully deleted the lookup value \"" + lookupValue.Name + "\".", "alert alert-success")
	return redirect(url_for("lookupValues.listLookupValues", lookupId = lookupValue.LookupId))

@lookupValues.route("/lookupValues/edit/<int:lookupValueId>", methods = ["GET", "POST"])
@adminRequired
def editLookupValue(lookupValueId):
	# check_admin()
	operation = "Edit"
	lookupValue = LookupValue.query.get_or_404(lookupValueId)
	lookup = Lookup.query.get_or_404(lookupValue.LookupId)
	form = LookupValueForm(obj = lookupValue)

	# Edit an existing lookupValue.
	if form.validate_on_submit():
		lookupValue.LookupId = form.lookupId.data
		lookupValue.Name = form.name.data
		lookupValue.Selectable = form.selectable.data
		lookupValue.Value = form.value.data
		db.session.commit()
		flash("You have successfully edited the lookup value \"" + lookupValue.Name + "\".", "alert alert-success")
		return redirect(url_for("lookupValues.listLookupValues", lookupId = lookupValue.LookupId))

	# Present a form to edit an existing lookupValue.
	form.lookupId.data = lookupValue.LookupId
	form.name.data = lookupValue.Name
	form.selectable.data = lookupValue.Selectable
	form.value.data = lookupValue.Value
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)
