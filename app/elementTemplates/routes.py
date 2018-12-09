from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from . import elementTemplates
from . forms import ElementTemplateForm
from .. import db
from .. decorators import adminRequired
from .. models import ElementAttributeTemplate, ElementTemplate, Enterprise, Site

modelName = "Element Template"

@elementTemplates.route("/elementTemplates/add/<int:siteId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def addElementTemplate(siteId):
	operation = "Add"
	form = ElementTemplateForm()

	# Add a new element template.
	if form.validate_on_submit():
		elementTemplate = ElementTemplate(Description = form.description.data, Name = form.name.data, SiteId = form.siteId.data)
		db.session.add(elementTemplate)
		db.session.commit()
		flash("You have successfully added the new element template \"{}\".".format(elementTemplate.Name), "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to add a new element template.
	form.siteId.data = siteId
	if form.requestReferrer.data is None:
		form.requestReferrer.data = request.referrer

	site = Site.query.get_or_404(siteId)
	breadcrumbs = [{"url" : url_for("elements.selectElement", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
		{"url" : url_for("elements.selectElement", selectedClass = "Enterprise", selectedId = site.Enterprise.EnterpriseId),
			"text" : site.Enterprise.Name},
		{"url" : url_for("elements.selectElement", selectedClass = "Site", selectedId = site.SiteId), "text" : site.Name}]
	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@elementTemplates.route("/elementTemplates/delete/<int:elementTemplateId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def deleteElementTemplate(elementTemplateId):
	elementTemplate = ElementTemplate.query.get_or_404(elementTemplateId)
	db.session.delete(elementTemplate)
	db.session.commit()
	flash("You have successfully deleted the element template \"{}\".".format(elementTemplate.Name), "alert alert-success")
	return redirect(request.referrer)

@elementTemplates.route("/elementTemplates/edit/<int:elementTemplateId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def editElementTemplate(elementTemplateId):
	operation = "Edit"
	elementTemplate = ElementTemplate.query.get_or_404(elementTemplateId)
	form = ElementTemplateForm(obj = elementTemplate)

	# Edit an existing element template.
	if form.validate_on_submit():
		elementTemplate.Description = form.description.data
		elementTemplate.Name = form.name.data
		elementTemplate.SiteId = form.siteId.data
		db.session.commit()
		flash("You have successfully edited the element template \"{}\".".format(elementTemplate.Name), "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to edit an existing element template.
	form.description.data = elementTemplate.Description
	form.name.data = elementTemplate.Name
	form.siteId.data = elementTemplate.SiteId
	if form.requestReferrer.data is None:
		form.requestReferrer.data = request.referrer

	breadcrumbs = [{"url" : url_for("elements.selectElement", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
		{"url" : url_for("elements.selectElement", selectedClass = "Enterprise", selectedId = elementTemplate.Site.Enterprise.EnterpriseId),
			"text" : elementTemplate.Site.Enterprise.Name},
		{"url" : url_for("elements.selectElement", selectedClass = "Site", selectedId = elementTemplate.Site.SiteId),
			"text" : elementTemplate.Site.Name},
		{"url" : None, "text" : elementTemplate.Name}]
	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)
