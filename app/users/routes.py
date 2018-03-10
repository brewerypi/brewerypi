from flask import flash, redirect, render_template, request, url_for
from . import users
from . forms import UserForm
from .. import db
from .. models import User

modelName = "User"

@users.route("/users/", methods = ["GET", "POST"])
#@login_required
def listUsers():
	users = User.query
	return render_template("users/users.html", users = users)

@users.route("/users/add", methods = ["GET", "POST"])
# @login_required
def addUser():
	# check_admin()
	operation = "Add"
	form = UserForm()

	# Add a new user.
	if form.validate_on_submit():
		user = User(Name = form.name.data, Password = form.password.data)
		db.session.add(user)
		db.session.commit()
		flash("You have successfully added the user \"" + user.Name + "\".", "alert alert-success")
		return redirect(url_for("users.listUsers"))

	# Present a form to add a new user.
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)

@users.route("/users/delete/<int:userId>", methods = ["GET", "POST"])
# @login_required
def deleteUser(userId):
	# check_admin()
	user = User.query.get_or_404(userId)
	db.session.delete(user)
	db.session.commit()
	flash("You have successfully deleted the user \"" + user.Name + "\".", "alert alert-success")
	return redirect(url_for("users.listUsers"))

@users.route("/users/edit/<int:userId>", methods = ["GET", "POST"])
# @login_required
def editUser(userId):
	# check_admin()
	operation = "Edit"
	user = User.query.get_or_404(userId)
	form = UserForm(obj = user)

	del form.name

	# Edit an existing user.
	if form.validate_on_submit():
		user.Password = form.password.data
		db.session.commit()
		flash("You have successfully edited the user \"" + user.Name + "\".", "alert alert-success")
		return redirect(url_for("users.listUsers"))

	# Present a form to edit an existing user.
	return render_template("addEditModel.html", form = form, modelName = modelName, operation = operation)
