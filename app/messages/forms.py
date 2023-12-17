from flask_wtf import FlaskForm
from wtforms import HiddenField, SelectMultipleField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

class MessageForm(FlaskForm):
	recipient = SelectMultipleField("To", validators = [DataRequired()], coerce = int)
	body = TextAreaField("Message", validators = [DataRequired()])
	requestReferrer = HiddenField()
	submit = SubmitField("Save")
