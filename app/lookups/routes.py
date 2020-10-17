from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from . import lookups
from . forms import LookupForm
from .. import db
from .. decorators import adminRequired
from .. models import Enterprise, Lookup, LookupValue

modelName = "Lookup"

@lookups.route("/lookups/add/<int:enterpriseId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def addLookup(enterpriseId):
	operation = "Add"
	form = LookupForm()

	# Add a new lookup.
	if form.validate_on_submit():
		lookup = Lookup(EnterpriseId = form.enterpriseId.data, Name = form.name.data)
		db.session.add(lookup)
		db.session.commit()
		flash("You have successfully added the lookup \"{}\".".format(lookup.Name), "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to add a new lookup.
	form.enterpriseId.data = enterpriseId
	if form.requestReferrer.data is None:
		form.requestReferrer.data = request.referrer

	enterprise = Enterprise.query.get_or_404(enterpriseId)
	breadcrumbs = [{"url" : url_for("lookups.selectLookup", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
		{"url" : url_for("lookups.selectLookup", selectedClass = "Enterprise", selectedId = enterprise.EnterpriseId), "text" : enterprise.Name}]
	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@lookups.route("/lookups/delete/<int:lookupId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def deleteLookup(lookupId):
	lookup = Lookup.query.get_or_404(lookupId)
	if lookup.isReferenced():
		flash('Lookup "{}" is referenced by one or more element and/or event frame attribute template and/or tag and cannot be deleted.'.format(lookup.Name),
			"alert alert-danger")
	else:
		lookup.delete()
		db.session.commit()
		flash('You have successfully deleted the lookup "{}".'.format(lookup.Name), "alert alert-success")

	return redirect(request.referrer)

@lookups.route("/lookups/edit/<int:lookupId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def editLookup(lookupId):
	operation = "Edit"
	lookup = Lookup.query.get_or_404(lookupId)
	form = LookupForm(obj = lookup)

	# Edit an existing lookup.
	if form.validate_on_submit():
		lookup.EnterpriseId = form.enterpriseId.data
		lookup.Name = form.name.data
		db.session.commit()
		flash("You have successfully edited the lookup \"{}\".".format(lookup.Name), "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to edit an existing lookup.
	form.lookupId.data = lookup.LookupId
	form.enterpriseId.data = lookup.EnterpriseId
	form.name.data = lookup.Name
	if form.requestReferrer.data is None:
		form.requestReferrer.data = request.referrer

	breadcrumbs = [{"url" : url_for("lookups.selectLookup", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
		{"url" : url_for("lookups.selectLookup", selectedClass = "Enterprise", selectedId = lookup.Enterprise.EnterpriseId), "text" : lookup.Enterprise.Name},
		{"url" : None, "text" : lookup.Name}]
	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@lookups.route("/lookups/select", methods = ["GET", "POST"]) # Default.
@lookups.route("/lookups/select/<string:selectedClass>", methods = ["GET", "POST"]) # Root.
@lookups.route("/lookups/select/<string:selectedClass>/<int:selectedId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def selectLookup(selectedClass = None, selectedId = None):
	if selectedClass == None:
		parent = Enterprise.query.join(Lookup).order_by(Enterprise.Name).first()
		if parent:
			children = Lookup.query.filter_by(EnterpriseId = parent.id())
		else:
			parent = Enterprise.query.order_by(Enterprise.Name).first()
			if parent is None:
				flash("You must create an Enterprise first.", "alert alert-danger")
				return redirect(request.referrer)

			children = None
		childrenClass = "Lookup"
	elif selectedClass == "Root":
		parent = None
		children = Enterprise.query.order_by(Enterprise.Name)
		childrenClass = "Enterprise"
	elif selectedClass == "Enterprise":
		parent = Enterprise.query.get_or_404(selectedId)
		children = Lookup.query.filter_by(EnterpriseId = selectedId)
		childrenClass = "Lookup"
	elif selectedClass == "Lookup":
		parent = Lookup.query.get_or_404(selectedId)
		children = LookupValue.query.filter_by(LookupId = selectedId)
		childrenClass = "LookupValue"

	return render_template("lookups/select.html", children = children, childrenClass = childrenClass, parent = parent)
