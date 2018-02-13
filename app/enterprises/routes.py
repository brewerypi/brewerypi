from flask import flash, redirect, render_template, request, url_for
from sqlalchemy import text
from . import enterprises
from . forms import EnterpriseForm
from .. import db
from .. models import Enterprise

modelName = "Enterprise"

@enterprises.route("/enterprises/", methods = ["GET", "POST"])
@enterprises.route("/enterprises/<string:sortColumn>", methods = ["GET", "POST"])
# @login_required
def listEnterprises(sortColumn = ""):
	if sortColumn != "":
		sortColumn = sortColumn + ", "
	enterprises = Enterprise.query.order_by(text(sortColumn + "Enterprise.Name"))
	return render_template("enterprises/enterprises.html", enterprises = enterprises)

@enterprises.route("/enterprises/add", methods = ["GET", "POST"])
# @login_required
def addEnterprise():
	# check_admin()
	operation = "Add"
	form = EnterpriseForm()

	# Add a new enterprise.
	if form.validate_on_submit():
		enterprise = Enterprise(Abbreviation = form.abbreviation.data, Description = form.description.data, Name = form.name.data)
		db.session.add(enterprise)
		db.session.commit()
		flash("You have successfully added the enterprise \"" + enterprise.Name + "\".", "alert alert-success")
		return redirect(url_for("enterprises.listEnterprises"))

	# Present a form to add a new enterprise.
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@enterprises.route("/enterprises/delete/<int:enterpriseId>", methods = ["GET", "POST"])
# @login_required
def deleteEnterprise(enterpriseId):
	# check_admin()
	enterprise = Enterprise.query.get_or_404(enterpriseId)
	db.session.delete(enterprise)
	db.session.commit()
	flash("You have successfully deleted the enterprise \"" + enterprise.Name + "\".", "alert alert-success")
	return redirect(url_for("enterprises.listEnterprises"))

@enterprises.route("/enterprises/edit/<int:enterpriseId>", methods = ["GET", "POST"])
# @login_required
def editEnterprise(enterpriseId):
	# check_admin()
	operation = "Edit"
	enterprise = Enterprise.query.get_or_404(enterpriseId)
	form = EnterpriseForm(obj = enterprise)

	# Edit an existing enterprise.
	if form.validate_on_submit():
		enterprise.Abbreviation = form.abbreviation.data
		enterprise.Description = form.description.data
		enterprise.Name = form.name.data
		db.session.commit()
		flash("You have successfully edited the enterprise \"" + enterprise.Name + "\".", "alert alert-success")
		return redirect(url_for("enterprises.listEnterprises"))

	# Present a form to edit an existing enterprise.
	form.abbreviation.data = enterprise.Abbreviation
	form.description.data = enterprise.Description
	form.name.data = enterprise.Name
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)
