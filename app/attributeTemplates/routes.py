from flask import flash, redirect, render_template, url_for
from sqlalchemy import text
from . import attributeTemplates
from . forms import AttributeTemplateForm
from .. import db
from .. models import AttributeTemplate, ElementTemplate, Enterprise, Site

modelName = "Attribute Template"

@attributeTemplates.route("/attributeTemplates", methods = ["GET", "POST"])
@attributeTemplates.route("/attributeTemplates/<string:sortColumn>", methods = ["GET", "POST"])
# @login_required
def listAttributeTemplates(sortColumn = ""):
	# check_admin()
	if sortColumn != "":
		sortColumn = sortColumn + ", "
	attributeTemplates = AttributeTemplate.query.join(ElementTemplate, Site, Enterprise). \
		order_by(text(sortColumn + "Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, AttributeTemplate.Name"))
	return render_template("attributeTemplates/attributeTemplates.html", attributeTemplates = attributeTemplates)

@attributeTemplates.route("/attributeTemplates/add", methods = ["GET", "POST"])
# @login_required
def addAttributeTemplate():
	# check_admin()
	operation = "Add"
	form = AttributeTemplateForm()

	# Add a new attributeTemplate.
	if form.validate_on_submit():
		attributeTemplate = AttributeTemplate(Description = form.description.data, ElementTemplate = form.elementTemplate.data, Name = form.name.data)
		db.session.add(attributeTemplate)
		db.session.commit()
		flash("You have successfully added the new attribute template \"" + attributeTemplate.Name + "\".")
		return redirect(url_for("attributeTemplates.listAttributeTemplates"))

	# Present a form to add a new attribute template.
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@attributeTemplates.route("/attributeTemplates/delete/<int:attributeTemplateId>", methods = ["GET", "POST"])
# @login_required
def deleteAttributeTemplate(attributeTemplateId):
	# check_admin()
	attributeTemplate = AttributeTemplate.query.get_or_404(attributeTemplateId)
	db.session.delete(attributeTemplate)
	db.session.commit()
	flash("You have successfully deleted the attribute template \"" + attributeTemplate.Name + "\".")
	return redirect(url_for("attributeTemplates.listAttributeTemplates"))

@attributeTemplates.route("/attributeTemplates/edit/<int:attributeTemplateId>", methods = ["GET", "POST"])
# @login_required
def editAttributeTemplate(attributeTemplateId):
	# check_admin()
	operation = "Edit"
	attributeTemplate = AttributeTemplate.query.get_or_404(attributeTemplateId)
	form = AttributeTemplateForm(obj = attributeTemplate)

	# Edit an existing attributeTemplate.
	if form.validate_on_submit():
		attributeTemplate.Description = form.description.data
		attributeTemplate.ElementTemplate = form.elementTemplate.data
		attributeTemplate.Name = form.name.data
		db.session.commit()
		flash("You have successfully edited the attribute template \"" + attributeTemplate.Name + "\".")
		return redirect(url_for("attributeTemplates.listAttributeTemplates"))

	# Present a form to edit an existing attributeTemplate.
	form.description.data = attributeTemplate.Description
	form.elementTemplate.data = attributeTemplate.ElementTemplate
	form.name.data = attributeTemplate.Name
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)
