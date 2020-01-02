from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from . import eventFrameGroups
from . forms import EventFrameGroupForm
from .. import db
from .. decorators import permissionRequired
from .. models import ElementTemplate, Enterprise, EventFrame, EventFrameEventFrameGroup, EventFrameGroup, EventFrameTemplate, EventFrameTemplateView, \
	Permission, Site

modelName = "Event Frame Group"

@eventFrameGroups.route("/eventFrameGroups/add", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def add():
	operation = "Add"
	form = EventFrameGroupForm()

	# Add a new event frame group.
	if form.validate_on_submit():
		eventFrameGroup = EventFrameGroup(Name = form.name.data)
		db.session.add(eventFrameGroup)
		db.session.commit()
		flash('You have successfully created the event frame group "{}".'.format(eventFrameGroup.Name), "alert alert-success")
		return redirect(url_for("eventFrameGroups.dashboard", eventFrameGroupId = eventFrameGroup.EventFrameGroupId))

	# Present a form to add a new event frame group.
	if form.requestReferrer.data is None:
		form.requestReferrer.data = request.referrer

	breadcrumbs = [{"url" : url_for("eventFrameGroups.listEventFrameGroups"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"}]
	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@eventFrameGroups.route("/eventFrameGroups/addActiveEventFrames/<int:eventFrameGroupId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def addActiveEventFrames(eventFrameGroupId):
	eventFrameGroup = EventFrameGroup.query.get_or_404(eventFrameGroupId)
	eventFrames = EventFrame.query.filter(EventFrame.EventFrameId.notin_([(eventFrameEventFrameGroup.EventFrameId) for eventFrameEventFrameGroup in
		eventFrameGroup.EventFrameEventFrameGroups]), EventFrame.EndTimestamp == None, EventFrame.ParentEventFrameId == None)
	return render_template("eventFrameGroups/addActiveEventFrames.html", eventFrameGroup = eventFrameGroup, eventFrames = eventFrames)

@eventFrameGroups.route("/eventFrameGroups/addNewEventFrames/<int:eventFrameGroupId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def addNewEventFrames(eventFrameGroupId):
	eventFrameGroup = EventFrameGroup.query.get_or_404(eventFrameGroupId)
	eventFrameTemplates = EventFrameTemplate.query.all()
	return render_template("eventFrameGroups/addNewEventFrames.html", eventFrameGroup = eventFrameGroup, eventFrameTemplates = eventFrameTemplates)

@eventFrameGroups.route("/eventFrameGroups/dashboard/<int:eventFrameGroupId>", methods = ["GET", "POST"])
@eventFrameGroups.route("/eventFrameGroups/dashboard/<int:eventFrameGroupId>/<int:displayEventFrameTemplateId>", methods = ["GET", "POST"])
@eventFrameGroups.route("/eventFrameGroups/dashboard/<int:eventFrameGroupId>/<int:displayEventFrameTemplateId>/<int:eventFrameTemplateViewId>",
	methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def dashboard(eventFrameGroupId, displayEventFrameTemplateId = None, eventFrameTemplateViewId = None):
	eventFrameGroup = EventFrameGroup.query.get_or_404(eventFrameGroupId)
	eventFrames = EventFrame.query.filter(EventFrame.EventFrameId. \
		in_([eventFrameEventFrameGroup.EventFrameId for eventFrameEventFrameGroup in eventFrameGroup.EventFrameEventFrameGroups]))
	eventFrameTemplates = EventFrameTemplate.query.join(ElementTemplate, Site, Enterprise).filter(EventFrameTemplate.EventFrameTemplateId. \
		in_([(eventFrame.EventFrameTemplateId) for eventFrame in eventFrames])).order_by(Enterprise.Name, Site.Name, ElementTemplate.Name,
		EventFrameTemplate.Name)
	if displayEventFrameTemplateId is None:
		displayEventFrameTemplate = eventFrameTemplates.first()
	else:
		displayEventFrameTemplate = EventFrameTemplate.query.get_or_404(displayEventFrameTemplateId)

	defaultEventFrameTemplateView = EventFrameTemplateView.query.filter_by(EventFrameTemplateId = displayEventFrameTemplate.EventFrameTemplateId,
		Default = True).one_or_none()
	if eventFrameTemplateViewId is None:
		if defaultEventFrameTemplateView is None:
			eventFrameTemplateView = None
			eventFrameAttributeTemplates = displayEventFrameTemplate.EventFrameAttributeTemplates
		else:
			eventFrameTemplateView = defaultEventFrameTemplateView
			eventFrameAttributeTemplates = [eventFrameAttributeTemplateEventFrameTemplateView.EventFrameAttributeTemplate for eventFrameAttributeTemplateEventFrameTemplateView in defaultEventFrameTemplateView.EventFrameAttributeTemplateEventFrameTemplateViews]
	elif eventFrameTemplateViewId == 0:
		eventFrameTemplateView = None
		eventFrameAttributeTemplates = displayEventFrameTemplate.EventFrameAttributeTemplates
	else:
		eventFrameTemplateView = EventFrameTemplateView.query.get_or_404(eventFrameTemplateViewId)
		eventFrameAttributeTemplates = [eventFrameAttributeTemplateEventFrameTemplateView.EventFrameAttributeTemplate for eventFrameAttributeTemplateEventFrameTemplateView in eventFrameTemplateView.EventFrameAttributeTemplateEventFrameTemplateViews]

	eventFrames = eventFrames.filter_by(EventFrameTemplate = displayEventFrameTemplate)
	return render_template("eventFrameGroups/dashboard.html", displayEventFrameTemplate = displayEventFrameTemplate, 
		eventFrameAttributeTemplates = eventFrameAttributeTemplates, eventFrames = eventFrames, eventFrameGroup = eventFrameGroup,
		eventFrameTemplates = eventFrameTemplates, eventFrameTemplateView = eventFrameTemplateView)

@eventFrameGroups.route("/eventFrameGroups/delete/<int:eventFrameGroupId>/<int:all>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def delete(eventFrameGroupId, all):
	eventFrameGroup = EventFrameGroup.query.get_or_404(eventFrameGroupId)
	if all == True:
		for eventFrameEventFrameGroup in eventFrameGroup.EventFrameEventFrameGroups:
			eventFrameEventFrameGroup.EventFrame.delete()

	eventFrameGroup.delete()
	db.session.commit()
	flash('You have successfully deleted the event frame group "{}".'.format(eventFrameGroup.Name), "alert alert-success")
	return redirect(request.referrer)

@eventFrameGroups.route("/eventFrameGroups/edit/<int:eventFrameGroupId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def edit(eventFrameGroupId):
	operation = "Edit"
	eventFrameGroup = EventFrameGroup.query.get_or_404(eventFrameGroupId)
	form = EventFrameGroupForm(obj = eventFrameGroup)

	# Edit and existing event frame group:
	if form.validate_on_submit():
		eventFrameGroup.Name = form.name.data
		db.session.commit()
		flash('You have successfully edited the event frame group "{}".'.format(eventFrameGroup.Name), "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to edit an existing event frame group.
	form.eventFrameGroupId.data = eventFrameGroup.EventFrameGroupId
	form.name.data = eventFrameGroup.Name
	if form.requestReferrer.data is None:
		form.requestReferrer.data = request.referrer

	breadcrumbs = [{"url" : url_for("eventFrameGroups.listEventFrameGroups"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
		{"url": None, "text": eventFrameGroup.Name}]
	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@eventFrameGroups.route("/eventFrameGroups", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def listEventFrameGroups():
	eventFrameGroups = EventFrameGroup.query.all()
	return render_template("eventFrameGroups/select.html", eventFrameGroups = eventFrameGroups)


@eventFrameGroups.route("/eventFrameGroups/endEventFrames/<int:eventFrameGroupId>", methods = ["GET", "POST"])
@eventFrameGroups.route("/eventFrameGroups/endEventFrames/<int:eventFrameGroupId>/<int:eventFrameTemplateId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def endEventFrames(eventFrameGroupId, eventFrameTemplateId = None):
	eventFrameGroup = EventFrameGroup.query.get_or_404(eventFrameGroupId)
	if eventFrameTemplateId is None:
		eventFrames = EventFrame.query.join(EventFrameEventFrameGroup).filter_by(EventFrameGroupId = eventFrameGroupId)
	else:
		eventFrameTemplate = EventFrameTemplate.query.get_or_404(eventFrameTemplateId)
		eventFrames = EventFrame.query.join(EventFrameEventFrameGroup).filter(EventFrame.EventFrameTemplateId == eventFrameTemplateId,
			EventFrameEventFrameGroup.EventFrameGroupId == eventFrameGroupId)

	for eventFrame in eventFrames:
		eventFrame.end()

	db.session.commit()
	if eventFrameTemplateId is None:
		flash('You have successfully ended the event frames in the "{}" event frame group.'.format(eventFrameGroup.Name), "alert alert-success")
	else:
		flash('You have successfully ended the "{}" event frames in the "{}" event frame group.'.format(eventFrameTemplate.Name, eventFrameGroup.Name),
			"alert alert-success")

	return redirect(request.referrer)

@eventFrameGroups.route("/eventFrameGroups/restartEventFrames/<int:eventFrameGroupId>", methods = ["GET", "POST"])
@eventFrameGroups.route("/eventFrameGroups/restartEventFrames/<int:eventFrameGroupId>/<int:eventFrameTemplateId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def restartEventFrames(eventFrameGroupId, eventFrameTemplateId = None):
	eventFrameGroup = EventFrameGroup.query.get_or_404(eventFrameGroupId)
	if eventFrameTemplateId is None:
		eventFrames = EventFrame.query.join(EventFrameEventFrameGroup).filter_by(EventFrameGroupId = eventFrameGroupId)
	else:
		eventFrameTemplate = EventFrameTemplate.query.get_or_404(eventFrameTemplateId)
		eventFrames = EventFrame.query.join(EventFrameEventFrameGroup).filter(EventFrame.EventFrameTemplateId == eventFrameTemplateId,
			EventFrameEventFrameGroup.EventFrameGroupId == eventFrameGroupId)

	for eventFrame in eventFrames:
		eventFrame.restart()

	db.session.commit()
	if eventFrameTemplateId is None:
		flash('You have successfully restarted the event frames in the "{}" event frame group.'.format(eventFrameGroup.Name), "alert alert-success")
	else:
		flash('You have successfully restarted the "{}" event frames in the "{}" event frame group.'.format(eventFrameTemplate.Name, eventFrameGroup.Name),
			"alert alert-success")

	return redirect(request.referrer)
