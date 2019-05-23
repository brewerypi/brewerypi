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
	form.recipient.choices = [(user.UserId, user.Name) for user in User.query.filter_by(Enabled = True).order_by(User.Name)]

	# Add a new message.
	if form.validate_on_submit():
		recipients = ""
		for recipient in form.recipient:
			if recipient.checked is True:
				recipient = User.query.get_or_404(recipient.data)
				if recipients == "":
					recipients = '"{}"'.format(recipient.Name)
				else:
					recipients = '{}, "{}"'.format(recipients, recipient.Name)

				message = Message(Body = form.body.data, Recipient = recipient, Sender = current_user)
				recipient.addNotification("unreadMessageCount", recipient.numberOfNewMessages())
				if eventFrameId is not None:
					message.Body = "<EventFrameId>{}</EventFrameId>{}".format(eventFrameId, message.Body)
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

				db.session.add(message)
				db.session.commit()

		flash('Your message to {} has been sent.'.format(recipients), "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to add a new message.
	if eventFrameId is not None:
		eventFrame = EventFrame.query.get_or_404(eventFrameId)
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
