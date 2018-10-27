from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from . import elementAttributeTemplates
from . forms import ElementAttributeTemplateForm
from .. import db
from .. decorators import adminRequired
from .. models import ElementAttributeTemplate, ElementTemplate, Enterprise, Site

modelName = "Element Attribute Template"

@elementAttributeTemplates.route("/elementAttributeTemplates/add/<int:elementTemplateId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def addElementAttributeTemplate(elementTemplateId):
	operation = "Add"
	form = ElementAttributeTemplateForm()

	# Add a new elementAttributeTemplate.
	if form.validate_on_submit():
		elementAttributeTemplate = ElementAttributeTemplate(Description = form.description.data, ElementTemplateId = form.elementTemplateId.data, \
			Name = form.name.data)
		db.session.add(elementAttributeTemplate)
		db.session.commit()
		flash("You have successfully added the new element attribute template \"{}\".".format(elementAttributeTemplate.Name), "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to add a new element attribute template.
	form.elementTemplateId.data = elementTemplateId
	form.requestReferrer.data = request.referrer
	elementTemplate = ElementTemplate.query.get_or_404(elementTemplateId)
	breadcrumbs = [{"url" : url_for("elements.selectElement", selectedClass = "Root"),
		"text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
		{"url" : url_for("elements.selectElement", selectedClass = "Enterprise", selectedId = elementTemplate.Site.Enterprise.EnterpriseId),
			"text" : elementTemplate.Site.Enterprise.Name},
		{"url" : url_for("elements.selectElement", selectedClass = "Site", selectedId = elementTemplate.Site.SiteId),
			"text" : elementTemplate.Site.Name},
		{"url" : url_for("elements.selectElement", selectedClass = "ElementAttributeTemplate", selectedId = elementTemplate.ElementTemplateId),
			"text" : elementTemplate.Name}]
	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@elementAttributeTemplates.route("/elementAttributeTemplates/delete/<int:elementAttributeTemplateId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def deleteElementAttributeTemplate(elementAttributeTemplateId):
	elementAttributeTemplate = ElementAttributeTemplate.query.get_or_404(elementAttributeTemplateId)
	db.session.delete(elementAttributeTemplate)
	db.session.commit()
	flash("You have successfully deleted the element attribute template \"{}\".".format(elementAttributeTemplate.Name), "alert alert-success")
	return redirect(request.referrer)

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
		elementAttributeTemplate.ElementTemplateId = form.elementTemplateId.data
		elementAttributeTemplate.Name = form.name.data
		db.session.commit()
		flash("You have successfully edited the element attribute template \"{}\".".format(elementAttributeTemplate.Name), "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to edit an existing elementAttributeTemplate.
	form.description.data = elementAttributeTemplate.Description
	form.elementTemplateId.data = elementAttributeTemplate.ElementTemplateId
	form.name.data = elementAttributeTemplate.Name
	form.requestReferrer.data = request.referrer
	breadcrumbs = [{"url" : url_for("elements.selectElement", selectedClass = "Root"),"text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
		{"url" : url_for("elements.selectElement", selectedClass = "Enterprise",
			selectedId = elementAttributeTemplate.ElementTemplate.Site.Enterprise.EnterpriseId),
			"text" : elementAttributeTemplate.ElementTemplate.Site.Enterprise.Name},
		{"url" : url_for("elements.selectElement", selectedClass = "Site", selectedId = elementAttributeTemplate.ElementTemplate.Site.SiteId),
			"text" : elementAttributeTemplate.ElementTemplate.Site.Name},
		{"url" : url_for("elements.selectElement", selectedClass = "ElementAttributeTemplate",
			selectedId = elementAttributeTemplate.ElementTemplate.ElementTemplateId),
			"text" : elementAttributeTemplate.ElementTemplate.Name},
		{"url" : None, "text" : elementAttributeTemplate.Name}]
	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)
