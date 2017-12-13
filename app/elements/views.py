from flask import redirect, render_template, url_for

from . import elements

from . forms import SelectElementForm

from .. import db

from .. models import Element, ElementTemplate, Enterprise, Site

@elements.route("/selectElement", methods = ["GET", "POST"])
# @login_required
def selectElement():
	# check_admin()

	form = SelectElementForm()

	if form.validate_on_submit():

		return redirect(url_for("elementAttributes.listElementAttributeValues", elementId = form.element.data.ElementId))

	# Present a form to select an element.
	return render_template("elements/selectElement.html", form = form)
