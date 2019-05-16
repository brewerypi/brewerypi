from datetime import datetime
from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from . import messages
from . forms import MessageForm
from .. import db
from .. models import EventFrame, Message, Notification, User

modelName = "Message"

@messages.route("/messages/add", methods = ["GET", "POST"])
@messages.route("/messages/eventFrame/add/<string:eventFrameId>", methods = ["GET", "POST"])
@login_required
def addMessage(eventFrameId = None):
	operation = "Add"
	form = MessageForm()

	# Add a new message.
	if form.validate_on_submit():
		recipient = User.query.get_or_404(form.recipient.data.UserId)
		message = Message(Body = form.body.data, Recipient = recipient, Sender = current_user)
		db.session.add(message)
		recipient.addNotification("unreadMessageCount", recipient.numberOfNewMessages())
		if eventFrameId is not None:
			notification = Notification.query.filter_by(Name = "unreadEventFrameMessageCount", User = recipient).one_or_none()
			if notification is None:
				dictionary = {eventFrameId: "1"}
			else:
				dictionary = notification.getPayload()
				if eventFrameId in dictionary:
					dictionary[eventFrameId] = int(dictionary[eventFrameId]) + 1
				else:
					dictionary[eventFrameId] = "1"

			recipient.addNotification("unreadEventFrameMessageCount", dictionary)

		db.session.commit()
		return redirect(form.requestReferrer.data)

		flash('Your message to "{}" has been sent.'.format(form.recipient.data.Name), "alert alert-success")
		return redirect(url_for("messages.listMessages"))

	# Present a form to add a new message.
	if eventFrameId is not None:
		eventFrame = EventFrame.query.get_or_404(eventFrameId)
		form.body.data = "Re: {} {} in element {} - ".format(eventFrame.EventFrameTemplate.Name, eventFrame.Name, eventFrame.Element.Name)
		breadcrumbs = [{"url": url_for("eventFrames.selectEventFrame", selectedClass = "Root"), "text": "<span class = \"glyphicon glyphicon-home\"></span>"},
			{"url": url_for("eventFrames.selectEventFrame", selectedClass = "Enterprise",
			selectedId = eventFrame.EventFrameTemplate.ElementTemplate.Site.Enterprise.EnterpriseId),
			"text": eventFrame.EventFrameTemplate.ElementTemplate.Site.Enterprise.Name},
			{"url": url_for("eventFrames.selectEventFrame", selectedClass = "Site", selectedId = eventFrame.EventFrameTemplate.ElementTemplate.Site.SiteId),
			"text": eventFrame.EventFrameTemplate.ElementTemplate.Site.Name}, {"url": url_for("eventFrames.selectEventFrame", selectedClass = "ElementTemplate",
			selectedId = eventFrame.EventFrameTemplate.ElementTemplate.ElementTemplateId), "text": eventFrame.EventFrameTemplate.ElementTemplate.Name},
			{"url": request.referrer, "text": eventFrame.EventFrameTemplate.Name},
			{"url": None, "text": eventFrame.Name}]
	else:
		breadcrumbs = [{"url" : url_for("messages.listMessages"), "text": "<span class = \"glyphicon glyphicon-home\"></span>"}]

	if form.requestReferrer.data is None:
		form.requestReferrer.data = request.referrer

	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@messages.route("/messages/delete/<int:messageId>", methods = ["GET", "POST"])
@login_required
def deleteMessage(messageId):
	message = Message.query.get_or_404(messageId)
	if message.RecipientId != current_user.UserId:
		abort(404)
	else:
		message.delete()
		db.session.commit()
		flash("You have successfully deleted the message.", "alert alert-success")
	return redirect(url_for("messages.listMessages"))

@messages.route("/messages", methods = ["GET", "POST"])
@login_required
def listMessages():
	current_user.LastMessageReadTimestamp = datetime.utcnow()
	current_user.addNotification("unreadMessageCount", 0)
	current_user.addNotification("unreadEventFrameMessageCount", {})
	db.session.commit()
	messages = Message.query.filter_by(RecipientId = current_user.UserId)
	return render_template("messages/messages.html", messages = messages)
