from flask import abort, flash, jsonify, redirect, render_template, request
from flask_login import current_user, login_required
from datetime import datetime
from . import eventFrameEventFrameGroups
from .. import db
from .. decorators import permissionRequired
from .. models import EventFrame, EventFrameEventFrameGroup, EventFrameGroup, EventFrameTemplate, Permission

@eventFrameEventFrameGroups.route("/eventFrameEventFrameGroups/add/<string:type>/<int:eventFrameGroupId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def add(type, eventFrameGroupId):
	data = request.get_json(force = True)
	count = 0
	for item in data:
		if type == "new":
			eventFrame = EventFrame(ElementId = item["elementId"], EventFrameTemplateId = item["eventFrameTemplateId"],
				Name = int(datetime.utcnow().timestamp()), StartTimestamp = datetime.utcnow(), UserId = current_user.get_id())
			db.session.add(eventFrame)
			db.session.commit()
			eventFrameEventFrameGroup = EventFrameEventFrameGroup(EventFrameGroupId = eventFrameGroupId, EventFrameId = eventFrame.EventFrameId)
			db.session.add(eventFrameEventFrameGroup)
			count = count + 1
		elif type == "active":
			eventFrameEventFrameGroup = EventFrameEventFrameGroup(EventFrameGroupId = eventFrameGroupId, EventFrameId = item["eventFrameId"])
			db.session.add(eventFrameEventFrameGroup)
			count = count + 1

	if count > 0:
		db.session.commit()
		message = "You have successfully added one or more event frames."
		flash(message, "alert alert-success")
	else:
		message = "Nothing added to save."
		flash(message, "alert alert-warning")
	return jsonify({"response": message})

@eventFrameEventFrameGroups.route("/eventFrameEventFrameGroups/delete/<int:eventFrameGroupId>/<int:eventFrameId>", methods = ["GET", "POST"])
@login_required
@permissionRequired(Permission.DATA_ENTRY)
def delete(eventFrameGroupId, eventFrameId):
	eventFrameEventFrameGroup = EventFrameEventFrameGroup.query.filter_by(EventFrameGroupId = eventFrameGroupId, EventFrameId = eventFrameId).one_or_none()
	if eventFrameEventFrameGroup is None:
		abort(404)

	eventFrameGroupName = eventFrameEventFrameGroup.EventFrameGroup.Name
	eventFrameName = eventFrameEventFrameGroup.EventFrame.Name
	eventFrameEventFrameGroup.delete()
	db.session.commit()
	flash('You have successfully removed the event frame "{}" from event frame group "{}".'.format(eventFrameName, eventFrameGroupName), "alert alert-success")
	return redirect(request.referrer)
