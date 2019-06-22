from flask_wtf import FlaskForm
from wtforms import HiddenField, SelectMultipleField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Required
from .. models import User

class MessageForm(FlaskForm):
	recipient = SelectMultipleField("To", validators = [Required()], coerce = int)
	body = TextAreaField("Message", validators = [DataRequired()])
	requestReferrer = HiddenField()
	submit = SubmitField("Save")
