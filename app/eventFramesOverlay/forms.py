from flask_wtf import FlaskForm
from wtforms import DateTimeField, HiddenField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Optional

class EventFramesOverlayForm(FlaskForm):
	startTimestamp = DateTimeField("Start", validators = [DataRequired()])
	startUtcTimestamp = HiddenField()
	endTimestamp = DateTimeField("End", validators = [Optional()])
	endUtcTimestamp = HiddenField()
	submit = SubmitField("Search")

	def validate_endTimestamp(self, field):
		if self.endTimestamp.data < self.startTimestamp.data:
			raise ValidationError("The End Timestamp must occur after the Start Timestamp.")
