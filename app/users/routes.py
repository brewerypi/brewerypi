from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, fresh_login_required, login_required, logout_user
from . import users
from . forms import UserForm
from .. import db
from .. decorators import adminRequired
from .. models import User

modelName = "User"

@users.route("/users", methods = ["GET", "POST"])
@login_required
@adminRequired
def listUsers():
	users = User.query.all()
	return render_template("users/users.html", users = users)

@users.route("/users/add", methods = ["GET", "POST"])
@adminRequired
def addUser():
	operation = "Add"
	form = UserForm()
	del form.currentPassword

	# Add a new user.
	if form.validate_on_submit():
		user = User(Enabled = form.enabled.data, Name = form.name.data, Password = form.password.data, Role = form.role.data)
		db.session.add(user)
		db.session.commit()
		flash('You have successfully added the user "{}".'.format(user.Name), "alert alert-success")
		return redirect(url_for("users.listUsers"))

	# Present a form to add a new user.
	breadcrumbs = [{"url" : url_for("users.listUsers"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"}]
	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@users.route("/users/changePassword/<int:userId>", methods = ["GET", "POST"])
@fresh_login_required
def changePassword(userId):
	# Only adminsitrators can change other user's password.
	if not current_user.isAdministrator() and current_user.get_id() != userId:
		abort(403)

	operation = "Edit"
	user = User.query.get_or_404(userId)
	form = UserForm(obj = user)
	# Don't require current password for administrators.
	if current_user.isAdministrator() and current_user.get_id() != userId:
		del form.currentPassword

	del form.name
	del form.role
	form.password.label.text = "New Password"
	form.password2.label.text = "Confirm New Password"

	# Change an existing user password.
	if form.validate_on_submit():
		user.Password = form.password.data
		db.session.commit()
		flash("You have successfully changed the password for user \"{}\".".format(user.Name), "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to change an user password.
	form.requestReferrer.data = request.referrer
	breadcrumbs = [{"url" : url_for("users.listUsers"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
		{"url" : None, "text" : user.Name}]
	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@users.route("/users/delete/<int:userId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def deleteUser(userId):
	user = User.query.get_or_404(userId)
	if user.Name == "pi":
		flash("Deleting the default administrator account is not allowed.", "alert alert-danger")
		return redirect(url_for("users.listUsers"))		

	if user.EventFrames.count() > 0 or user.MessagesReceived.count() > 0 or user.MessagesSent.count() > 0 or user.Notes.count() > 0 or \
		user.TagValues.count() > 0:
		flash('User "{}" has event frames, messages, notes and/or tag values and cannot be deleted.'.format(user.Name), "alert alert-danger")
		return redirect(url_for("users.listUsers"))

	user.delete()
	db.session.commit()
	flash("You have successfully deleted the user \"{}\".".format(user.Name), "alert alert-success")
	if current_user.UserId == userId:
		logout_user()
		return redirect(url_for("main.index"))
	else:
		return redirect(url_for("users.listUsers"))

@users.route("/users/edit/<int:userId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def editUser(userId):
	user = User.query.get_or_404(userId)
	if user.Name == "pi":
		flash("Editing the default administrator account is not allowed.", "alert alert-danger")
		return redirect(url_for("users.listUsers"))		

	operation = "Edit"
	form = UserForm(obj = user)
	del form.currentPassword
	del form.password
	del form.password2

	# Edit an existing user.
	if form.validate_on_submit():
		user.Name = form.name.data
		user.Role = form.role.data
		user.Enabled = form.enabled.data
		db.session.commit()
		flash("You have successfully edited the user \"{}\".".format(user.Name), "alert alert-success")
		return redirect(url_for("users.listUsers"))

	# Present a form to edit an existing user.
	form.userId.data = user.UserId
	form.name.data = user.Name
	form.role.data = user.Role
	form.enabled.data = user.Enabled
	if form.requestReferrer.data is None:
		form.requestReferrer.data = request.referrer

	breadcrumbs = [{"url" : url_for("users.listUsers"), "text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
		{"url" : None, "text" : user.Name}]
	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@users.route("/users/enableDisable/<int:userId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def enableDisableUser(userId):
	user = User.query.get_or_404(userId)
	if user.Name == "pi":
		flash("Disabling the default administrator account is not allowed.", "alert alert-danger")
		return redirect(url_for("users.listUsers"))		

	user.Enabled = not user.Enabled
	db.session.commit()
	flash('You have successfully {} the user "{}".'.format("enabled" if user.Enabled else "disabled", user.Name), "alert alert-success")
	if current_user.UserId == userId:
		logout_user()
		return redirect(url_for("main.index"))
	else:
		return redirect(url_for("users.listUsers"))
