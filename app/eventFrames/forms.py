from flask_wtf import FlaskForm
from datetime import datetime
from wtforms import DateTimeField, HiddenField, SelectField, StringField, SubmitField, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Required, Optional
from .. models import EventFrame

class EventFrameForm(FlaskForm):
	element = QuerySelectField("Element", validators = [Required()], get_label = "Name")
	eventFrameTemplate = QuerySelectField("Event Frame Template", validators = [Required()], get_label = "Name")
	startTimestamp = DateTimeField("Start Timestamp", default = datetime.now, validators = [Required()])
	endTimestamp = DateTimeField("End Timestamp", validators = [Optional()])
	name = StringField("Name", validators = [Optional()])
	eventFrameTemplateId = HiddenField()
	parentEventFrameId = HiddenField()
	requestReferrer = HiddenField()
	submit = SubmitField("Save")

	def validate_endTimestamp(self, field):
		if self.endTimestamp.data < self.startTimestamp.data:
			raise ValidationError("The End Timestamp must occur after the Start Timestamp.")

		if self.parentEventFrameId.data:
			parentEventFrame = EventFrame.query.get_or_404(self.parentEventFrameId.data)
			error = False
			if parentEventFrame.EndTimestamp:
				if self.endTimestamp.data > parentEventFrame.EndTimestamp:
					raise ValidationError("This timestamp is outside of the parent event frame.")

	def validate_startTimestamp(self, field):
		if self.parentEventFrameId.data:
			parentEventFrame = EventFrame.query.get_or_404(self.parentEventFrameId.data)
			error = False
			if parentEventFrame.EndTimestamp:
				if self.startTimestamp.data < parentEventFrame.StartTimestamp or self.startTimestamp.data > parentEventFrame.EndTimestamp:
					error = True
			else:
				if self.startTimestamp.data < parentEventFrame.StartTimestamp:
					error = True

			if error:
				raise ValidationError("This timestamp is outside of the parent event frame.")

class EventFrameOverlayForm(FlaskForm):
	startTimestamp = DateTimeField("Start", validators = [Required()])
	endTimestamp = DateTimeField("End", validators = [Optional()])
	submit = SubmitField("Search")

	def validate_endTimestamp(self, field):
		if self.endTimestamp.data < self.startTimestamp.data:
			raise ValidationError("The End Timestamp must occur after the Start Timestamp.")