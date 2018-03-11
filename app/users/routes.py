from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
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
	users = User.query
	return render_template("users/users.html", users = users)

@users.route("/users/add", methods = ["GET", "POST"])
@adminRequired
def addUser():
	operation = "Add"
	form = UserForm()

	# Add a new user.
	if form.validate_on_submit():
		user = User(Name = form.name.data, Password = form.password.data, Role = form.role.data)
		db.session.add(user)
		db.session.commit()
		flash("You have successfully added the user \"" + user.Name + "\".", "alert alert-success")
		return redirect(url_for("users.listUsers"))

	# Present a form to add a new user.
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@users.route("/users/delete/<int:userId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def deleteUser(userId):
	user = User.query.get_or_404(userId)
	db.session.delete(user)
	db.session.commit()
	flash("You have successfully deleted the user \"" + user.Name + "\".", "alert alert-success")
	return redirect(url_for("users.listUsers"))

@users.route("/users/changePassword/<int:userId>", methods = ["GET", "POST"])
@login_required
def changePassword(userId):
	operation = "Edit"
	user = User.query.get_or_404(userId)
	form = UserForm(obj = user)

	del form.name
	del form.role

	# Edit an existing user.
	if form.validate_on_submit():
		user.Password = form.password.data
		db.session.commit()
		flash("You have successfully changed the password for user \"" + user.Name + "\".", "alert alert-success")
		return redirect(form.requestReferrer.data)

	# Present a form to edit an existing user.
	form.requestReferrer.data = request.referrer
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@users.route("/users/edit/<int:userId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def editUser(userId):
	operation = "Edit"
	user = User.query.get_or_404(userId)
	form = UserForm(obj = user)

	del form.password
	del form.password2

	# Edit an existing user.
	if form.validate_on_submit():
		user.Name = form.name.data
		user.Role = form.role.data
		db.session.commit()
		flash("You have successfully edited the user \"" + user.Name + "\".", "alert alert-success")
		return redirect(url_for("users.listUsers"))

	# Present a form to edit an existing user.
	form.userId.data = user.UserId
	form.name.data = user.Name
	form.role.data = user.Role
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)
