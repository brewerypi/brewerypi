from . import notifications
from app.models import Notification
from flask import jsonify, request
from flask_login import current_user, login_required

@notifications.route("/notifications/get")
@login_required
def getNotifications():
	since = request.args.get("since", 0.0, type = float)
	notifications = current_user.Notifications.filter(Notification.UnixTimestamp > since).order_by(Notification.UnixTimestamp.asc())
	return jsonify([{"name": notification.Name, "data": notification.getPayload(), "UnixTimestamp": notification.UnixTimestamp}
		for notification in notifications])