from flask_wtf import FlaskForm
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms import PasswordField, StringField, SubmitField, ValidationError
from wtforms.validators import EqualTo, Length, Regexp, Required
from .. models import Role, User

class UserForm(FlaskForm):
	name = StringField("Username", validators = [Length(1, 45), Regexp("^[A-Za-z][A-Za-z0-9_.]*$", 0,
		"Usernames must have only letters, numbers, dots or underscore."), Required()])
	role = QuerySelectField(query_factory = lambda: Role.query.order_by(Role.Name), get_label = "Name")
	password = PasswordField("Password", validators = [EqualTo("password2", message = "Passwords must match."), Required()])
	password2 = PasswordField("Confirm Password", validators = [Required()])
	submit = SubmitField("Save")

	def validate_name(self, field):
		if User.query.filter_by(Name = field.data).first():
			raise ValidationError("Username already exists.")
