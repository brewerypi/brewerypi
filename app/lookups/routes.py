from flask import flash, redirect, render_template, request, url_for
from . import lookups
from . forms import LookupForm
from .. import db
from .. decorators import adminRequired
from .. models import Enterprise, Lookup

modelName = "Lookup"

@lookups.route("/lookups", methods = ["GET", "POST"])
@adminRequired
def listLookups():
	# check_admin()
	lookups = Lookup.query
	return render_template("lookups/lookups.html", lookups = lookups)

@lookups.route("/lookups/add", methods = ["GET", "POST"])
@adminRequired
def addLookup():
	# check_admin()
	operation = "Add"
	form = LookupForm()

	# Add a new lookup.
	if form.validate_on_submit():
		lookup = Lookup(Enterprise = form.enterprise.data, Name = form.name.data)
		db.session.add(lookup)
		db.session.commit()
		flash("You have successfully added the lookup \"" + lookup.Name + "\".", "alert alert-success")
		return redirect(url_for("lookups.listLookups"))

	# Present a form to add a new lookup.
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@lookups.route("/lookups/delete/<int:lookupId>", methods = ["GET", "POST"])
@adminRequired
def deleteLookup(lookupId):
	# check_admin()
	lookup = Lookup.query.get_or_404(lookupId)
	db.session.delete(lookup)
	db.session.commit()
	flash("You have successfully deleted the lookup \"" + lookup.Name + "\".", "alert alert-success")
	return redirect(url_for("lookups.listLookups"))

@lookups.route("/lookups/edit/<int:lookupId>", methods = ["GET", "POST"])
@adminRequired
def editLookup(lookupId):
	# check_admin()
	operation = "Edit"
	lookup = Lookup.query.get_or_404(lookupId)
	form = LookupForm(obj = lookup)

	# Edit an existing lookup.
	if form.validate_on_submit():
		lookup.Enterprise = form.enterprise.data
		lookup.Name = form.name.data
		db.session.commit()
		flash("You have successfully edited the lookup \"" + lookup.Name + "\".", "alert alert-success")
		return redirect(url_for("lookups.listLookups"))

	# Present a form to edit an existing lookup.
	form.enterprise.data = lookup.Enterprise
	form.name.data = lookup.Name
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)
