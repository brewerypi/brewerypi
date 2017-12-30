from flask import flash, redirect, render_template, request, url_for
from . import elementTemplates
from . forms import ElementTemplateForm
from .. import db
from .. models import ElementTemplate, Enterprise, Site

modelName = "Element Template"

@elementTemplates.route("/elementTemplates", methods = ["GET", "POST"])
# @login_required
def listElementTemplates():
	# check_admin()
	elementTemplates = ElementTemplate.query.join(Site, Enterprise).order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name)
	return render_template("elementTemplates/elementTemplates.html", elementTemplates = elementTemplates)

@elementTemplates.route("/elementTemplates/add", methods = ["GET", "POST"])
# @login_required
def addElementTemplate():
	# check_admin()
	operation = "Add"
	form = ElementTemplateForm()

	# Add a new element template.
	if form.validate_on_submit():
		elementTemplate = ElementTemplate(Description = form.description.data, Name = form.name.data, Site = form.site.data)
		db.session.add(elementTemplate)
		db.session.commit()
		flash("You have successfully added the new element template \"" + elementTemplate.Name + "\".")
		return redirect(url_for("elementTemplates.listElementTemplates"))

	# Present a form to add a new element template.
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@elementTemplates.route("/elementTemplates/delete/<int:elementTemplateId>", methods = ["GET", "POST"])
# @login_required
def deleteElementTemplate(elementTemplateId):
	# check_admin()
	elementTemplate = ElementTemplate.query.get_or_404(elementTemplateId)
	db.session.delete(elementTemplate)
	db.session.commit()
	flash("You have successfully deleted the element template \"" + elementTemplate.Name + "\".")
	return redirect(url_for("elementTemplates.listElementTemplates"))

@elementTemplates.route("/elementTemplates/edit/<int:elementTemplateId>", methods = ["GET", "POST"])
# @login_required
def editElementTemplate(elementTemplateId):
	# check_admin()
	operation = "Edit"
	elementTemplate = ElementTemplate.query.get_or_404(elementTemplateId)
	form = ElementTemplateForm(obj = elementTemplate)

	# Edit an existing element template.
	if form.validate_on_submit():
		elementTemplate.Description = form.description.data
		elementTemplate.Name = form.name.data
		elementTemplate.Site = form.site.data
		db.session.commit()
		flash("You have successfully edited the element template \"" + elementTemplate.Name + "\".")
		return redirect(url_for("elementTemplates.listElementTemplates"))

	# Present a form to edit an existing element template.
	form.description.data = elementTemplate.Description
	form.name.data = elementTemplate.Name
	form.site.data = elementTemplate.Site
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)
