from flask import flash, redirect, render_template, url_for
from . import elements
from . forms import ElementForm, SelectElementForm
from .. import db
from .. models import AttributeTemplate, Element, ElementAttribute, ElementTemplate, Enterprise, Site

modelName = "Element"

@elements.route("/elements", methods = ["GET", "POST"])
# @login_required
def listElements():
	# check_admin()
	elements = Element.query.join(ElementTemplate, Site, Enterprise).order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, Element.Name)
	return render_template("elements/elements.html", elements = elements)

@elements.route("/elements/<int:elementId>", methods = ["GET", "POST"])
# @login_required
def dashboard(elementId):
	# check_admin()
	element = Element.query.get_or_404(elementId)
	elementAttributes = ElementAttribute.query. \
		join(AttributeTemplate). \
		filter(ElementAttribute.ElementId == elementId). \
		order_by(AttributeTemplate.Name)
	return render_template("elements/elementDashboard.html", elementAttributes = elementAttributes, elementName = element.Name)

@elements.route("/elements/add", methods = ["GET", "POST"])
# @login_required
def addElement():
	# check_admin()
	operation = "Add"
	form = ElementForm()

	# Add a new element.
	if form.validate_on_submit():
		element = Element(Description = form.description.data, ElementTemplate = form.elementTemplate.data, Name = form.name.data)
		db.session.add(element)
		db.session.commit()
		flash("You have successfully added the new element \"" + element.Name + "\".")
		return redirect(url_for("elements.listElements"))

	# Present a form to add a new element.
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@elements.route("/elements/delete/<int:elementId>", methods = ["GET", "POST"])
# @login_required
def deleteElement(elementId):
	# check_admin()
	element = Element.query.get_or_404(elementId)
	db.session.delete(element)
	db.session.commit()
	flash("You have successfully deleted the element \"" + element.Name + "\".")
	return redirect(url_for("elements.listElements"))

@elements.route("/elements/edit/<int:elementId>", methods = ["GET", "POST"])
# @login_required
def editElement(elementId):
	# check_admin()
	operation = "Edit"
	element = Element.query.get_or_404(elementId)
	form = ElementForm(obj = element)

	# Edit an existing element.
	if form.validate_on_submit():
		element.Description = form.description.data
		element.ElementTemplate = form.elementTemplate.data
		element.Name = form.name.data

		db.session.commit()
		flash("You have successfully edited the element \"" + element.Name + "\".")
		return redirect(url_for("elements.listElements"))

	# Present a form to edit an existing element.
	form.description.data = element.Description
	form.elementTemplate.data = element.ElementTemplate
	form.name.data = element.Name
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@elements.route("/selectElement", methods = ["GET", "POST"])
# @login_required
def selectElement():
	# check_admin()
	form = SelectElementForm()

	if form.validate_on_submit():
		# return redirect(url_for("elementAttributes.listElementAttributeValues", elementId = form.element.data.ElementId))
		return redirect(url_for("elements.dashboard", elementId = form.element.data.ElementId))

	# Present a form to select an element.
	return render_template("elements/selectElement.html", form = form)
