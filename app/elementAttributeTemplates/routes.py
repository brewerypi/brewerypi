from flask import flash, redirect, render_template, url_for
from flask_login import login_required
from . import elementAttributeTemplates
from . forms import ElementAttributeTemplateForm
from .. import db
from .. decorators import adminRequired
from .. models import ElementAttributeTemplate, ElementTemplate, Enterprise, Site

modelName = "Element Attribute Template"

@elementAttributeTemplates.route("/elementAttributeTemplates", methods = ["GET", "POST"])
@login_required
@adminRequired
def listElementAttributeTemplates():
	elementAttributeTemplates = ElementAttributeTemplate.query.all()
	return render_template("elementAttributeTemplates/elementAttributeTemplates.html", elementAttributeTemplates = elementAttributeTemplates)

@elementAttributeTemplates.route("/elementAttributeTemplates/add", methods = ["GET", "POST"])
@login_required
@adminRequired
def addElementAttributeTemplate():
	operation = "Add"
	form = ElementAttributeTemplateForm()

	# Add a new elementAttributeTemplate.
	if form.validate_on_submit():
		elementAttributeTemplate = ElementAttributeTemplate(Description = form.description.data, ElementTemplate = form.elementTemplate.data, \
			Name = form.name.data)
		db.session.add(elementAttributeTemplate)
		db.session.commit()
		flash("You have successfully added the new element attribute template \"" + elementAttributeTemplate.Name + "\".", "alert alert-success")
		return redirect(url_for("elementAttributeTemplates.listElementAttributeTemplates"))

	# Present a form to add a new element attribute template.
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@elementAttributeTemplates.route("/elementAttributeTemplates/delete/<int:elementAttributeTemplateId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def deleteElementAttributeTemplate(elementAttributeTemplateId):
	elementAttributeTemplate = ElementAttributeTemplate.query.get_or_404(elementAttributeTemplateId)
	db.session.delete(elementAttributeTemplate)
	db.session.commit()
	flash("You have successfully deleted the element attribute template \"" + elementAttributeTemplate.Name + "\".", "alert alert-success")
	return redirect(url_for("elementAttributeTemplates.listElementAttributeTemplates"))

@elementAttributeTemplates.route("/elementAttributeTemplates/edit/<int:elementAttributeTemplateId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def editElementAttributeTemplate(elementAttributeTemplateId):
	operation = "Edit"
	elementAttributeTemplate = ElementAttributeTemplate.query.get_or_404(elementAttributeTemplateId)
	form = ElementAttributeTemplateForm(obj = elementAttributeTemplate)

	# Edit an existing elementAttributeTemplate.
	if form.validate_on_submit():
		elementAttributeTemplate.Description = form.description.data
		elementAttributeTemplate.ElementTemplate = form.elementTemplate.data
		elementAttributeTemplate.Name = form.name.data
		db.session.commit()
		flash("You have successfully edited the element attribute template \"" + elementAttributeTemplate.Name + "\".", "alert alert-success")
		return redirect(url_for("elementAttributeTemplates.listElementAttributeTemplates"))

	# Present a form to edit an existing elementAttributeTemplate.
	form.description.data = elementAttributeTemplate.Description
	form.elementTemplate.data = elementAttributeTemplate.ElementTemplate
	form.name.data = elementAttributeTemplate.Name
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)
