from flask_wtf import FlaskForm
from datetime import datetime
from wtforms import DateTimeField, HiddenField, SelectField, StringField, SubmitField, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Required, Optional
from .. models import Element, EventFrame

class EventFrameForm(FlaskForm):
	element = QuerySelectField("Element", validators = [Required()], get_label = "Name")
	eventFrameTemplate = QuerySelectField("Event Frame Template", validators = [Required()], get_label = "Name")
	startTimestamp = DateTimeField("Start Timestamp", default = datetime.utcnow, validators = [Required()])
	startUtcTimestamp = HiddenField()
	endTimestamp = DateTimeField("End Timestamp", validators = [Optional()])
	endUtcTimestamp = HiddenField()
	name = StringField("Name", default = lambda : int(datetime.utcnow().timestamp()), validators = [Required()])
	eventFrameTemplateId = HiddenField()
	parentEventFrameId = HiddenField()
	requestReferrer = HiddenField()
	submit = SubmitField("Save")

	def validate_endTimestamp(self, field):
		if self.startTimestamp.data is not None and self.endTimestamp.data is not None:
			if self.endTimestamp.data < self.startTimestamp.data:
				raise ValidationError("The End Timestamp must occur after the Start Timestamp.")

			if self.parentEventFrameId.data:
				parentEventFrame = EventFrame.query.get_or_404(self.parentEventFrameId.data)
				if parentEventFrame.EndTimestamp:
					endUtcTimestamp = datetime.strptime(self.endUtcTimestamp.data, "%Y-%m-%d %H:%M:%S")
					if endUtcTimestamp > parentEventFrame.EndTimestamp:
						raise ValidationError("This timestamp is outside of the parent event frame.")

	def validate_startTimestamp(self, field):
		if self.startTimestamp.data is not None:
			if self.parentEventFrameId.data:
				startUtcTimestamp = datetime.strptime(self.startUtcTimestamp.data, "%Y-%m-%d %H:%M:%S")
				parentEventFrame = EventFrame.query.get_or_404(self.parentEventFrameId.data)
				error = False
				if parentEventFrame.EndTimestamp:
					if startUtcTimestamp < parentEventFrame.StartTimestamp or startUtcTimestamp > parentEventFrame.EndTimestamp:
						error = True
				else:
					if startUtcTimestamp < parentEventFrame.StartTimestamp:
						error = True

				if error:
					raise ValidationError("This timestamp is outside of the parent event frame.")

class EventFrameOverlayForm(FlaskForm):
	startTimestamp = DateTimeField("Start", validators = [Required()])
	startUtcTimestamp = HiddenField()
	endTimestamp = DateTimeField("End", validators = [Optional()])
	endUtcTimestamp = HiddenField()
	submit = SubmitField("Search")

	def validate_endTimestamp(self, field):
		if self.endTimestamp.data < self.startTimestamp.data:
			raise ValidationError("The End Timestamp must occur after the Start Timestamp.")
