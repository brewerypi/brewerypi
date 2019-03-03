from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from . import eventFrameAttributeTemplates
from . forms import EventFrameAttributeTemplateForm
from .. import db
from .. decorators import adminRequired
from .. models import EventFrameAttributeTemplate, EventFrameTemplate

modelName = "Event Frame Attribute Template"

@eventFrameAttributeTemplates.route("/eventFrameAttributeTemplates/add/eventFrameTemplateId/<int:eventFrameTemplateId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def addEventFrameAttributeTemplate(eventFrameTemplateId):
	operation = "Add"
	form = EventFrameAttributeTemplateForm()

	# Add a new eventFrameAttributeTemplate
	if form.validate_on_submit():
		eventFrameAttributeTemplate = EventFrameAttributeTemplate(Description = form.description.data, EventFrameTemplateId = eventFrameTemplateId, 
			Name = form.name.data)
		db.session.add(eventFrameAttributeTemplate)
		db.session.commit()
		flash("You have successfully added the new event frame attribute template \"{}\" to the event frame template \"{}\".". \
			format(eventFrameAttributeTemplate.Name, eventFrameAttributeTemplate.EventFrameTemplate.Name), "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to add a new event frame attribute template.
	form.eventFrameTemplateId.data = eventFrameTemplateId
	if form.requestReferrer.data is None:
		form.requestReferrer.data = request.referrer

	eventFrameTemplate = EventFrameTemplate.query.get_or_404(eventFrameTemplateId)
	if eventFrameTemplate.hasParent():
		breadcrumbs = [{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Enterprise",
				selectedId = eventFrameTemplate.origin().ElementTemplate.Site.Enterprise.EnterpriseId),
				"text" : eventFrameTemplate.origin().ElementTemplate.Site.Enterprise.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Site",
				selectedId = eventFrameTemplate.origin().ElementTemplate.Site.SiteId), "text" : eventFrameTemplate.origin().ElementTemplate.Site.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "ElementTemplate",
				selectedId = eventFrameTemplate.origin().ElementTemplate.ElementTemplateId), "text" : eventFrameTemplate.origin().ElementTemplate.Name}]
		for eventFrameTemplateAcestor in eventFrameTemplate.ancestors([]):
			breadcrumbs.append({"url" : url_for("eventFrames.selectEventFrame", selectedClass = "EventFrame",
				selectedId = eventFrameTemplateAcestor.EventFrameTemplateId), "text" : eventFrameTemplateAcestor.Name})

		breadcrumbs.append({"url" : url_for("eventFrames.selectEventFrame", selectedClass = "EventFrame",
			selectedId = eventFrameTemplate.EventFrameTemplateId),
			"text" : eventFrameTemplate.Name})
	else:
		breadcrumbs = [{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Enterprise",
				selectedId = eventFrameTemplate.ElementTemplate.Site.Enterprise.EnterpriseId),
				"text" : eventFrameTemplate.ElementTemplate.Site.Enterprise.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Site",
				selectedId = eventFrameTemplate.ElementTemplate.Site.SiteId),
				"text" : eventFrameTemplate.ElementTemplate.Site.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "ElementTemplate",
				selectedId = eventFrameTemplate.ElementTemplate.ElementTemplateId), "text" : eventFrameTemplate.ElementTemplate.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "EventFrameTemplate",
				selectedId = eventFrameTemplate.EventFrameTemplateId, selectedOperation = "configure"),
				"text" : eventFrameTemplate.Name}]

	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@eventFrameAttributeTemplates.route("/eventFrameAttributeTemplates/delete/eventFrameAttributeTemplateId/<int:eventFrameAttributeTemplateId>",
	methods = ["GET", "POST"])
@login_required
@adminRequired
def deleteEventFrameAttributeTemplate(eventFrameAttributeTemplateId):
	eventFrameAttributeTemplate = EventFrameAttributeTemplate.query.get_or_404(eventFrameAttributeTemplateId)
	eventFrameAttributeTemplate.delete()
	db.session.commit()
	flash("You have successfully deleted the event frame attribute template \"{}\".".format(eventFrameAttributeTemplate.Name), "alert alert-success")
	return redirect(request.referrer)

@eventFrameAttributeTemplates.route("/eventFrameAttributeTemplates/edit/eventFrameAttributeTemplateId/<int:eventFrameAttributeTemplateId>",
	methods = ["GET", "POST"])
@login_required
@adminRequired
def editEventFrameAttributeTemplate(eventFrameAttributeTemplateId):
	operation = "Edit"
	eventFrameAttributeTemplate = EventFrameAttributeTemplate.query.get_or_404(eventFrameAttributeTemplateId)
	eventFrameTemplateId = eventFrameAttributeTemplate.EventFrameTemplate.EventFrameTemplateId
	form = EventFrameAttributeTemplateForm(obj = eventFrameAttributeTemplate)

	# Edit an existing eventFrameAttributeTemplate.
	if form.validate_on_submit():
		eventFrameAttributeTemplate.Description = form.description.data
		eventFrameAttributeTemplate.Name = form.name.data
		db.session.commit()
		flash("You have successfully edited the event frame attribute template \"" + eventFrameAttributeTemplate.Name + "\".", "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to edit an existing eventFrameAttributeTemplate.
	form.eventFrameAttributeTemplateId.data = eventFrameAttributeTemplate.EventFrameAttributeTemplateId
	form.description.data = eventFrameAttributeTemplate.Description
	form.eventFrameTemplateId.data = eventFrameAttributeTemplate.EventFrameTemplateId
	form.name.data = eventFrameAttributeTemplate.Name
	if form.requestReferrer.data is None:
		form.requestReferrer.data = request.referrer

	if eventFrameAttributeTemplate.EventFrameTemplate.hasParent():
		breadcrumbs = [{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Enterprise",
				selectedId = eventFrameAttributeTemplate.EventFrameTemplate.origin().ElementTemplate.Site.Enterprise.EnterpriseId),
				"text" : eventFrameAttributeTemplate.EventFrameTemplate.origin().ElementTemplate.Site.Enterprise.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Site",
				selectedId = eventFrameAttributeTemplate.EventFrameTemplate.origin().ElementTemplate.Site.SiteId),
				"text" : eventFrameAttributeTemplate.EventFrameTemplate.origin().ElementTemplate.Site.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "ElementTemplate",
				selectedId = eventFrameAttributeTemplate.EventFrameTemplate.origin().ElementTemplate.ElementTemplateId),
				"text" : eventFrameAttributeTemplate.EventFrameTemplate.origin().ElementTemplate.Name}]
		for eventFrameTemplateAcestor in eventFrameAttributeTemplate.EventFrameTemplate.ancestors([]):
			breadcrumbs.append({"url" : url_for("eventFrames.selectEventFrame", selectedClass = "EventFrameTemplate",
				selectedId = eventFrameTemplateAcestor.EventFrameTemplateId, selectedOperation = "configure"), "text" : eventFrameTemplateAcestor.Name})

		breadcrumbs.extend([{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "EventFrameTemplate",
			selectedId = eventFrameAttributeTemplate.EventFrameTemplate.EventFrameTemplateId, selectedOperation = "configure"),
			"text" : eventFrameAttributeTemplate.EventFrameTemplate.Name}, {"url" : None, "text" : eventFrameAttributeTemplate.Name}])
	else:
		breadcrumbs = [{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Enterprise",
				selectedId = eventFrameAttributeTemplate.EventFrameTemplate.ElementTemplate.Site.Enterprise.EnterpriseId),
				"text" : eventFrameAttributeTemplate.EventFrameTemplate.ElementTemplate.Site.Enterprise.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Site",
				selectedId = eventFrameAttributeTemplate.EventFrameTemplate.ElementTemplate.Site.SiteId),
				"text" : eventFrameAttributeTemplate.EventFrameTemplate.ElementTemplate.Site.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "ElementTemplate",
				selectedId = eventFrameAttributeTemplate.EventFrameTemplate.ElementTemplate.ElementTemplateId),
				"text" : eventFrameAttributeTemplate.EventFrameTemplate.ElementTemplate.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "EventFrameTemplate",
				selectedId = eventFrameAttributeTemplate.EventFrameTemplate.EventFrameTemplateId, selectedOperation = "configure"),
				"text" : eventFrameAttributeTemplate.EventFrameTemplate.Name},
			{"url" : None, "text" : eventFrameAttributeTemplate.Name}]

	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)
