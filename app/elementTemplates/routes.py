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
		flash("You have successfully added the new element template \"" + elementTemplate.Name + "\".", "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to add a new element template.
	form.siteId.data = siteId
	form.requestReferrer.data = request.referrer
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@elementTemplates.route("/elementTemplates/delete/<int:elementTemplateId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def deleteElementTemplate(elementTemplateId):
	elementTemplate = ElementTemplate.query.get_or_404(elementTemplateId)
	db.session.delete(elementTemplate)
	db.session.commit()
	flash("You have successfully deleted the element template \"" + elementTemplate.Name + "\".", "alert alert-success")
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
		flash("You have successfully edited the element template \"" + elementTemplate.Name + "\".", "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to edit an existing element template.
	form.description.data = elementTemplate.Description
	form.name.data = elementTemplate.Name
	form.siteId.data = elementTemplate.SiteId
	form.requestReferrer.data = request.referrer
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@elementTemplates.route("/elementTemplates/select", methods = ["GET", "POST"]) # Default.
@elementTemplates.route("/elementTemplates/select/<string:selectedClass>", methods = ["GET", "POST"]) # Root.
@elementTemplates.route("/elementTemplates/select/<string:selectedClass>/<int:selectedId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def selectElementTemplate(selectedClass = None, selectedId = None):
	if selectedClass == None:
		parent = Site.query.join(Enterprise).order_by(Enterprise.Name, Site.Name).first()
		if parent:
			children = ElementTemplate.query.join(Site).filter_by(SiteId = parent.id()).order_by(ElementTemplate.Name)
		else:
			children = None
		childrenClass = "ElementTemplate"
	elif selectedClass == "Root":
		parent = None
		children = Enterprise.query.order_by(Enterprise.Name)
		childrenClass = "Enterprise"
	elif selectedClass == "Enterprise":
		parent = Enterprise.query.get_or_404(selectedId)
		children = Site.query.join(Enterprise).filter_by(EnterpriseId = selectedId).order_by(Site.Name)
		childrenClass = "Site"
	elif selectedClass == "Site":
		parent = Site.query.get_or_404(selectedId)
		children = ElementTemplate.query.join(Site).filter_by(SiteId = selectedId).order_by(ElementTemplate.Name)
		childrenClass = "ElementTemplate"
	elif selectedClass == "ElementTemplate":
		parent = ElementTemplate.query.get_or_404(selectedId)
		children = ElementAttributeTemplate.query.join(ElementTemplate).filter_by(ElementTemplateId = selectedId).order_by(ElementAttributeTemplate.Name)
		childrenClass = "ElementAttributeTemplate"

	return render_template("elementTemplates/select.html", children = children, childrenClass = childrenClass, parent = parent)
