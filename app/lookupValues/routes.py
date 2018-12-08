from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from . import lookupValues
from . forms import LookupValueForm
from .. import db
from .. decorators import adminRequired
from .. models import Lookup, LookupValue

modelName = "Lookup Value"

@lookupValues.route("/lookupValues/add/<int:lookupId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def addLookupValue(lookupId):
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
		flash("You have successfully added the new lookup value \"{}\".".format(lookupValue.Name), "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to add a new lookupValue.
	form.lookupId.data = lookupId
	form.selectable.data = True
	if form.requestReferrer.data is None:
		# If request.referrer is None (i.e. if accessing add/edit from a bookmark), will return to home page
		form.requestReferrer.data = request.referrer
	lookup = Lookup.query.get_or_404(lookupId)
	breadcrumbs = [{"url" : url_for("lookups.selectLookup", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
		{"url" : url_for("lookups.selectLookup", selectedClass = "Enterprise", selectedId = lookup.Enterprise.EnterpriseId), "text" : lookup.Enterprise.Name},
		{"url" : url_for("lookups.selectLookup", selectedClass = "Lookup", selectedId = lookup.LookupId), "text" : lookup.Name}]
	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@lookupValues.route("/lookupValues/delete/<int:lookupValueId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def deleteLookupValue(lookupValueId):
	lookupValue = LookupValue.query.get_or_404(lookupValueId)
	if lookupValue.isReferenced():
		flash("Lookup value \"{}\" is referenced by one or more tag values and cannot be deleted.".format(lookupValue.Name), "alert alert-danger")
	else:
		db.session.delete(lookupValue)
		db.session.commit()
		flash("You have successfully deleted the lookup value \"{}\".".format(lookupValue.Name), "alert alert-success")

	return redirect(request.referrer)

@lookupValues.route("/lookupValues/edit/<int:lookupValueId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def editLookupValue(lookupValueId):
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
		flash("You have successfully edited the lookup value \"{}\".".format(lookupValue.Name), "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to edit an existing lookupValue.
	form.lookupId.data = lookupValue.LookupId
	form.name.data = lookupValue.Name
	form.selectable.data = lookupValue.Selectable
	form.value.data = lookupValue.Value
	if form.requestReferrer.data is None:
		# If request.referrer is None (i.e. if accessing add/edit from a bookmark), will return to home page
		form.requestReferrer.data = request.referrer
	breadcrumbs = [{"url" : url_for("lookups.selectLookup", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
		{"url" : url_for("lookups.selectLookup", selectedClass = "Enterprise", selectedId = lookup.Enterprise.EnterpriseId), "text" : lookup.Enterprise.Name},
		{"url" : url_for("lookups.selectLookup", selectedClass = "Lookup", selectedId = lookup.LookupId), "text" : lookup.Name},
		{"url" : None, "text" : lookupValue.Name}]
	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)
