from datetime import datetime
from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from . import messages
from . forms import MessageForm
from .. import db
from .. models import Message

modelName = "Message"

@messages.route("/messages/add", methods = ["GET", "POST"])
@login_required
def addMessage():
	form = MessageForm()

	# Add a new message.
	if form.validate_on_submit():
		message = Message(Body = form.body.data, Recipient = form.recipient.data, Sender = current_user)
		db.session.add(message)
		form.recipient.data.addNotification("unreadMessageCount", form.recipient.data.numberOfNewMessages())
		db.session.commit()
		flash('Your message to "{}" has been sent.'.format(form.recipient.data.Name), "alert alert-success")
		return redirect(url_for("messages.listMessages"))

	breadcrumbs = [{"url" : url_for("messages.listMessages"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"}]
	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form)

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
	db.session.commit()
	messages = Message.query.filter_by(RecipientId = current_user.UserId)
	return render_template("messages/messages.html", messages = messages)
