import json
from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import login_required
from . import eventFrameTemplateViews
from . forms import CopyEventFrameTemplateViewForm, EventFrameTemplateViewForm
from .. import db
from .. decorators import adminRequired
from .. models import EventFrameAttributeTemplate, EventFrameTemplate, EventFrameTemplateView, EventFrameAttributeTemplateEventFrameTemplateView

modelName = "Event Frame Template View"

@eventFrameTemplateViews.route("/eventFrameTemplateViews/add/<int:eventFrameTemplateId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def add(eventFrameTemplateId):
	operation = "Add"
	form = EventFrameTemplateViewForm()

	# Add a new event frame template view.
	if form.validate_on_submit():
		default = form.default.data
		if default is True:
			for defaultEventFrameTemplateView in EventFrameTemplateView.query.filter_by(Default = True, EventFrameTemplateId = eventFrameTemplateId):
				defaultEventFrameTemplateView.Default = False
			
			db.session.commit()

		eventFrameTemplateViewMaximumOrder = EventFrameTemplateView.query.filter_by(EventFrameTemplateId = eventFrameTemplateId). \
			order_by(EventFrameTemplateView.Order.desc()).first()
		if eventFrameTemplateViewMaximumOrder is None:
			order = 1
		else:
			order = eventFrameTemplateViewMaximumOrder.Order + 1

		eventFrameTemplateView = EventFrameTemplateView(Default = default, Description = form.description.data, EventFrameTemplateId = eventFrameTemplateId,
			Name = form.name.data, Selectable = True if default else form.selectable.data, Order = order)
		db.session.add(eventFrameTemplateView)
		db.session.commit()
		flash('You have successfully added the new event frame template view "{}".'.format(eventFrameTemplateView.Name), "alert alert-success")
		return redirect(url_for("eventFrameTemplateViews.eventFrameAttributeTemplates",
			eventFrameTemplateViewId = eventFrameTemplateView.EventFrameTemplateViewId))

	# Present a form to add a new event frame template view.
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
			breadcrumbs.append({"url" : url_for("eventFrames.selectEventFrame", selectedClass = "EventFrameTemplate",
				selectedId = eventFrameTemplateAcestor.EventFrameTemplateId, selectedOperation = "configure"), "text" : eventFrameTemplateAcestor.Name})

		breadcrumbs.append({"url" : url_for("eventFrames.selectEventFrame", selectedClass = "EventFrameTemplate",
			selectedId = eventFrameTemplate.EventFrameTemplateId, selectedOperation = "configure"), "text" : eventFrameTemplate.Name})
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

@eventFrameTemplateViews.route("/eventFrameTemplateViews/copy/<int:fromEventFrameTemplateViewId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def copy(fromEventFrameTemplateViewId):
	operation = "Copy"
	form = CopyEventFrameTemplateViewForm()
	fromEventFrameTemplateView = EventFrameTemplateView.query.get_or_404(fromEventFrameTemplateViewId)
	if form.validate_on_submit():
		default = form.default.data
		if default is True:
			for defaultEventFrameTemplateView in EventFrameTemplateView.query.filter_by(Default = True,
				EventFrameTemplateId = fromEventFrameTemplateView.EventFrameTemplateId):
				defaultEventFrameTemplateView.Default = False
			
			db.session.commit()

		eventFrameTemplateViewMaximumOrder = EventFrameTemplateView.query.filter_by(EventFrameTemplateId = fromEventFrameTemplateView.EventFrameTemplateId). \
			order_by(EventFrameTemplateView.Order.desc()).first()
		if eventFrameTemplateViewMaximumOrder is None:
			order = 1
		else:
			order = eventFrameTemplateViewMaximumOrder.Order + 1

		eventFrameTemplateView = EventFrameTemplateView(Default = default, Description = form.description.data,
			Dictionary = fromEventFrameTemplateView.Dictionary, EventFrameTemplateId = fromEventFrameTemplateView.EventFrameTemplateId,
			Name = form.name.data, Order = order, Selectable = True if default else fromEventFrameTemplateView.Selectable)
		db.session.add(eventFrameTemplateView)
		db.session.commit()
		for fromEventFrameAttributeTemplateEventFrameTemplateView in fromEventFrameTemplateView.EventFrameAttributeTemplateEventFrameTemplateViews:
			eventFrameAttributeTemplateEventFrameTemplateView = EventFrameAttributeTemplateEventFrameTemplateView( \
				EventFrameAttributeTemplateId = fromEventFrameAttributeTemplateEventFrameTemplateView.EventFrameAttributeTemplateId,
				EventFrameTemplateViewId = eventFrameTemplateView.EventFrameTemplateViewId,
				Order = fromEventFrameAttributeTemplateEventFrameTemplateView.Order)
			db.session.add(eventFrameAttributeTemplateEventFrameTemplateView)

		db.session.commit()
		flash(f'You have successfully copied the event frame template view "{fromEventFrameTemplateView.Name}" to "{eventFrameTemplateView.Name}".',
			"alert alert-success")
		return redirect(url_for("eventFrameTemplateViews.eventFrameAttributeTemplates",
			eventFrameTemplateViewId = eventFrameTemplateView.EventFrameTemplateViewId))

	# Present a form to copy an event frame template view.
	form.eventFrameTemplateId.data = fromEventFrameTemplateView.EventFrameTemplateId
	breadcrumbs = []
	if fromEventFrameTemplateView.EventFrameTemplate.hasParent():
		breadcrumbs = [{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Enterprise",
				selectedId = fromEventFrameTemplateView.EventFrameTemplate.origin().ElementTemplate.Site.Enterprise.EnterpriseId),
				"text" : fromEventFrameTemplateView.EventFrameTemplate.origin().ElementTemplate.Site.Enterprise.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Site",
				selectedId = fromEventFrameTemplateView.EventFrameTemplate.origin().ElementTemplate.Site.SiteId),
				"text" : fromEventFrameTemplateView.EventFrameTemplate.origin().ElementTemplate.Site.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "ElementTemplate",
				selectedId = fromEventFrameTemplateView.EventFrameTemplate.origin().ElementTemplate.ElementTemplateId),
				"text" : fromEventFrameTemplateView.EventFrameTemplate.origin().ElementTemplate.Name}]
		for eventFrameTemplateAcestor in fromEventFrameTemplateView.EventFrameTemplate.ancestors([]):
			breadcrumbs.append({"url" : url_for("eventFrames.selectEventFrame", selectedClass = "EventFrameTemplate",
				selectedId = eventFrameTemplateAcestor.EventFrameTemplateId, selectedOperation = "configure"), "text" : eventFrameTemplateAcestor.Name})

		breadcrumbs.extend([{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "EventFrameTemplate",
			selectedId = fromEventFrameTemplateView.EventFrameTemplate.EventFrameTemplateId, selectedOperation = "configure"),
			"text" : fromEventFrameTemplateView.EventFrameTemplate.Name}, {"url" : None, "text" : fromEventFrameTemplateView.Name}])
	else:
		breadcrumbs = [{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Enterprise",
				selectedId = fromEventFrameTemplateView.EventFrameTemplate.ElementTemplate.Site.Enterprise.EnterpriseId),
				"text" : fromEventFrameTemplateView.EventFrameTemplate.ElementTemplate.Site.Enterprise.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Site",
				selectedId = fromEventFrameTemplateView.EventFrameTemplate.ElementTemplate.Site.SiteId),
				"text" : fromEventFrameTemplateView.EventFrameTemplate.ElementTemplate.Site.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "ElementTemplate",
				selectedId = fromEventFrameTemplateView.EventFrameTemplate.ElementTemplate.ElementTemplateId),
				"text" : fromEventFrameTemplateView.EventFrameTemplate.ElementTemplate.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "EventFrameTemplate",
				selectedId = fromEventFrameTemplateView.EventFrameTemplate.EventFrameTemplateId, selectedOperation = "configure"),
				"text" : fromEventFrameTemplateView.EventFrameTemplate.Name},
			{"url" : None, "text" : fromEventFrameTemplateView.Name}]

	if form.requestReferrer.data is None:
		form.requestReferrer.data = request.referrer

	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@eventFrameTemplateViews.route("/eventFrameTemplateViews/delete/<int:eventFrameTemplateViewId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def delete(eventFrameTemplateViewId):
	eventFrameTemplateView = EventFrameTemplateView.query.get_or_404(eventFrameTemplateViewId)
	eventFrameTemplateView.delete()
	db.session.commit()
	flash('You have successfully deleted the event frame template view "{}".'.format(eventFrameTemplateView.Name), "alert alert-success")
	return redirect(request.referrer)

@eventFrameTemplateViews.route("/eventFrameTemplateViews/edit/<int:eventFrameTemplateViewId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def edit(eventFrameTemplateViewId):
	operation = "Edit"
	eventFrameTemplateView = EventFrameTemplateView.query.get_or_404(eventFrameTemplateViewId)
	form = EventFrameTemplateViewForm(obj = eventFrameTemplateView)

	# Edit an existing event frame template view.
	if form.validate_on_submit():
		default = form.default.data
		if default is True:
			for defaultEventFrameTemplateView in EventFrameTemplateView.query.filter_by(Default = True,
				EventFrameTemplateId = eventFrameTemplateView.EventFrameTemplateId):
				defaultEventFrameTemplateView.Default = False

			db.session.commit()

		eventFrameTemplateView.Description = form.description.data
		eventFrameTemplateView.Default = default
		eventFrameTemplateView.EventFrameTemplateId = form.eventFrameTemplateId.data
		eventFrameTemplateView.Name = form.name.data
		eventFrameTemplateView.Selectable = True if default else form.selectable.data
		db.session.commit()
		flash('You have successfully edited the event frame template view "{}".'.format(eventFrameTemplateView.Name), "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to edit an existing event frame template view.
	form.default.data = eventFrameTemplateView.Default
	form.description.data = eventFrameTemplateView.Description
	form.eventFrameTemplateId.data = eventFrameTemplateView.EventFrameTemplateId
	form.eventFrameTemplateViewId.data = eventFrameTemplateView.EventFrameTemplateViewId
	form.name.data = eventFrameTemplateView.Name
	form.selectable.data = eventFrameTemplateView.Selectable
	if form.requestReferrer.data is None:
		form.requestReferrer.data = request.referrer

	if eventFrameTemplateView.EventFrameTemplate.hasParent():
		breadcrumbs = [{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Enterprise",
				selectedId = eventFrameTemplateView.EventFrameTemplate.origin().ElementTemplate.Site.Enterprise.EnterpriseId),
				"text" : eventFrameTemplateView.EventFrameTemplate.origin().ElementTemplate.Site.Enterprise.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Site",
				selectedId = eventFrameTemplateView.EventFrameTemplate.origin().ElementTemplate.Site.SiteId),
				"text" : eventFrameTemplateView.EventFrameTemplate.origin().ElementTemplate.Site.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "ElementTemplate",
				selectedId = eventFrameTemplateView.EventFrameTemplate.origin().ElementTemplate.ElementTemplateId),
				"text" : eventFrameTemplateView.EventFrameTemplate.origin().ElementTemplate.Name}]
		for eventFrameTemplateAcestor in eventFrameTemplateView.EventFrameTemplate.ancestors([]):
			breadcrumbs.append({"url" : url_for("eventFrames.selectEventFrame", selectedClass = "EventFrameTemplate",
				selectedId = eventFrameTemplateAcestor.EventFrameTemplateId, selectedOperation = "configure"), "text" : eventFrameTemplateAcestor.Name})

		breadcrumbs.extend([{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "EventFrameTemplate",
			selectedId = eventFrameTemplateView.EventFrameTemplate.EventFrameTemplateId, selectedOperation = "configure"),
			"text" : eventFrameTemplateView.EventFrameTemplate.Name}, {"url" : None, "text" : eventFrameTemplateView.Name}])
	else:
		breadcrumbs = [{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Root"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Enterprise",
				selectedId = eventFrameTemplateView.EventFrameTemplate.ElementTemplate.Site.Enterprise.EnterpriseId),
				"text" : eventFrameTemplateView.EventFrameTemplate.ElementTemplate.Site.Enterprise.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "Site",
				selectedId = eventFrameTemplateView.EventFrameTemplate.ElementTemplate.Site.SiteId),
				"text" : eventFrameTemplateView.EventFrameTemplate.ElementTemplate.Site.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "ElementTemplate",
				selectedId = eventFrameTemplateView.EventFrameTemplate.ElementTemplate.ElementTemplateId),
				"text" : eventFrameTemplateView.EventFrameTemplate.ElementTemplate.Name},
			{"url" : url_for("eventFrames.selectEventFrame", selectedClass = "EventFrameTemplate",
				selectedId = eventFrameTemplateView.EventFrameTemplate.EventFrameTemplateId, selectedOperation = "configure"),
				"text" : eventFrameTemplateView.EventFrameTemplate.Name},
			{"url" : None, "text" : eventFrameTemplateView.Name}]

	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@eventFrameTemplateViews.route("/eventFrameTemplateViews/editEventFrameAttributeTemplates/<int:eventFrameTemplateViewId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def editEventFrameAttributeTemplates(eventFrameTemplateViewId):
	eventFrameTemplateView = EventFrameTemplateView.query.get_or_404(eventFrameTemplateViewId)
	data = request.get_json(force = True)
	dictionary = data[0]
	incomingEventFrameAttributeTemplates = data[1]
	eventFrameTemplateView.Dictionary = dictionary
	for eventFrameAttributeTemplateEventFrameTemplateView in eventFrameTemplateView.EventFrameAttributeTemplateEventFrameTemplateViews:
		eventFrameAttributeTemplateEventFrameTemplateView.delete()

	db.session.commit()
	for incomingEventFrameAttributeTemplateId in incomingEventFrameAttributeTemplates:
		eventFrameAttributeTemplateEventFrameTemplateView = \
			EventFrameAttributeTemplateEventFrameTemplateView(EventFrameAttributeTemplateId = incomingEventFrameAttributeTemplateId,
			EventFrameTemplateViewId = eventFrameTemplateViewId, Order = incomingEventFrameAttributeTemplates[incomingEventFrameAttributeTemplateId])
		db.session.add(eventFrameAttributeTemplateEventFrameTemplateView)

	db.session.commit()
	message = 'You have successfully updated the event frame template view "{}".'.format(eventFrameTemplateView.Name)
	flash(message, "alert alert-success")
	return jsonify({"response": message})

@eventFrameTemplateViews.route("/eventFrameTemplateViews/eventFrameAttributeTemplates/<int:eventFrameTemplateViewId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def eventFrameAttributeTemplates(eventFrameTemplateViewId):
	eventFrameTemplateView = EventFrameTemplateView.query.get_or_404(eventFrameTemplateViewId)
	allEventFrameAttributeTemplatesIds = [eventFrameAttributeTemplate.EventFrameAttributeTemplateId
		for eventFrameAttributeTemplate in eventFrameTemplateView.EventFrameTemplate.EventFrameAttributeTemplates]

	includedEventFrameAttributeTemplateIds = [eventFrameAttributeTemplateEventFrameTemplateView.EventFrameAttributeTemplateId
		for eventFrameAttributeTemplateEventFrameTemplateView in eventFrameTemplateView.EventFrameAttributeTemplateEventFrameTemplateViews]

	excludedEventFrameAttributeTemplateIds = list(set(allEventFrameAttributeTemplatesIds) - set(includedEventFrameAttributeTemplateIds))
	excludedEventFrameAttributeTemplates = EventFrameAttributeTemplate.query. \
		filter(EventFrameAttributeTemplate.EventFrameAttributeTemplateId.in_(excludedEventFrameAttributeTemplateIds))
	return render_template("eventFrameTemplateViews/eventFrameAttributeTemplates.html", dictionary = eventFrameTemplateView.dictionary(),
		eventFrameTemplateView = eventFrameTemplateView, excludedEventFrameAttributeTemplates = excludedEventFrameAttributeTemplates)

@eventFrameTemplateViews.route("/eventFrameTemplateViews/reorder/<int:eventFrameTemplateId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def reorder(eventFrameTemplateId):
	incomingEventFrameTemplateViews = request.get_json(force = True)
	for eventFrameTemplateViewId in incomingEventFrameTemplateViews:
		eventFrameTemplateView = EventFrameTemplateView.query.get_or_404(eventFrameTemplateViewId)
		eventFrameTemplateView.Order = incomingEventFrameTemplateViews[eventFrameTemplateViewId]

	db.session.commit()
	return jsonify()
