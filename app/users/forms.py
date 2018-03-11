from flask_wtf import FlaskForm
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms import HiddenField, PasswordField, StringField, SubmitField, ValidationError
from wtforms.validators import EqualTo, Length, Regexp, Required
from .. models import Role, User

class UserForm(FlaskForm):
	userId = HiddenField()
	name = StringField("Username", validators = [Length(1, 45), Regexp("^[A-Za-z][A-Za-z0-9_.]*$", 0,
		"Usernames must have only letters, numbers, dots or underscore."), Required()])
	role = QuerySelectField(query_factory = lambda: Role.query.order_by(Role.Name), get_label = "Name")
	password = PasswordField("Password", validators = [EqualTo("password2", message = "Passwords must match."), Required()])
	password2 = PasswordField("Confirm Password", validators = [Required()])
	requestReferrer = HiddenField()
	submit = SubmitField("Save")

	def validate_name(self, field):
		user = User.query.filter_by(Name = field.data).first()
		if user:
			if self.userId.data == "":
				# Trying to add a new user with a name that already exists.
				raise ValidationError("Username already exists.")
			else:
				if int(self.userId.data) != user.UserId:
				# Trying to change the name of an user to a name that already exists.
					raise ValidationError("Username already exists.")
