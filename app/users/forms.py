from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, PasswordField, StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length, Regexp 
from wtforms_sqlalchemy.fields import QuerySelectField
from .. models import Role, User

class UserForm(FlaskForm):
	name = StringField("Username", validators = [Length(1, 45), Regexp("^[A-Za-z][A-Za-z0-9_.]*$", 0,
		"Usernames must start with a letter and then only have letters, numbers, dots or underscores."), DataRequired()])
	role = QuerySelectField(query_factory = lambda: Role.query.order_by(Role.Name), get_label = "Name")
	currentPassword = PasswordField("Current Password", validators = [DataRequired()])
	password = PasswordField("Password", validators = [EqualTo("password2", message = "Passwords must match."), DataRequired()])
	password2 = PasswordField("Confirm Password", validators = [DataRequired()])
	enabled = BooleanField("Enabled", default = "checked")
	userId = HiddenField()
	requestReferrer = HiddenField()
	submit = SubmitField("Save")

	def validate_currentPassword(self, field):
		if not current_user.verifyPassword(field.data):
			raise ValidationError("Current password is incorrect.")

	def validate_name(self, field):
		validationError = False
		user = User.query.filter_by(Name = field.data).one_or_none()
		if user is not None:
			# User exists.
			if self.userId.data == "":
				# Trying to add a new user using a name that already exists.
				validationError = True
			else:
				if int(self.userId.data) != user.UserId:
					# Trying to change the name of an user to a name that already exists.
					validationError = True

		if validationError:
			raise ValidationError('Username "{}" already exists.'.format(field.data))
