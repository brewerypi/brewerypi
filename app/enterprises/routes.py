from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from . import enterprises
from . forms import EnterpriseForm
from .. import db
from .. decorators import adminRequired
from .. models import Enterprise

modelName = "Enterprise"

@enterprises.route("/enterprises/add", methods = ["GET", "POST"])
@login_required
@adminRequired
def addEnterprise():
	operation = "Add"
	form = EnterpriseForm()

	# Add a new enterprise.
	if form.validate_on_submit():
		enterprise = Enterprise(Abbreviation = form.abbreviation.data, Description = form.description.data, Name = form.name.data)
		db.session.add(enterprise)
		db.session.commit()
		flash("You have successfully added the enterprise \"{}\".".format(enterprise.Name), "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to add a new enterprise.
	form.requestReferrer.data = request.referrer
	breadcrumbs = [{"url" : url_for("physicalModels.selectPhysicalModel", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\">"}]
	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@enterprises.route("/enterprises/delete/<int:enterpriseId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def deleteEnterprise(enterpriseId):
	enterprise = Enterprise.query.get_or_404(enterpriseId)
	db.session.delete(enterprise)
	db.session.commit()
	flash("You have successfully deleted the enterprise \"{}\".".format(enterprise.Name), "alert alert-success")
	return redirect(request.referrer)

@enterprises.route("/enterprises/edit/<int:enterpriseId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def editEnterprise(enterpriseId):
	operation = "Edit"
	enterprise = Enterprise.query.get_or_404(enterpriseId)
	form = EnterpriseForm(obj = enterprise)

	# Edit an existing enterprise.
	if form.validate_on_submit():
		enterprise.Abbreviation = form.abbreviation.data
		enterprise.Description = form.description.data
		enterprise.Name = form.name.data
		db.session.commit()
		flash("You have successfully edited the enterprise \"{}\".".format(enterprise.Name), "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to edit an existing enterprise.
	form.abbreviation.data = enterprise.Abbreviation
	form.description.data = enterprise.Description
	form.name.data = enterprise.Name
	form.requestReferrer.data = request.referrer
	breadcrumbs = [{"url" : url_for("physicalModels.selectPhysicalModel", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\">"},
		{"url" : None, "text" : enterprise.Name}]
	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)
