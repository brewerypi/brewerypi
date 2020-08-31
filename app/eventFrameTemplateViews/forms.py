from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, StringField, SubmitField, ValidationError
from wtforms.validators import Length, Required
from .. models import EventFrameTemplateView

class EventFrameTemplateViewForm(FlaskForm):
	name = StringField("Name", validators = [Required(), Length(1, 45)])
	description = StringField("Description", validators = [Length(0, 255)])
	default = BooleanField("Default")
	selectable = BooleanField("Selectable", default = "checked")
	eventFrameTemplateId = HiddenField()
	eventFrameTemplateViewId = HiddenField()
	requestReferrer = HiddenField()
	submit = SubmitField("Save")

	def validate_name(self, field):
		validationError = False
		eventFrameTemplateView = EventFrameTemplateView.query.filter_by(EventFrameTemplateId = self.eventFrameTemplateId.data, Name = field.data).first()
		if eventFrameTemplateView is not None:
			if self.eventFrameTemplateViewId.data == "":
				# Trying to add a new event frame template view using a name that already exists.
				validationError = True
			else:
				if int(self.eventFrameTemplateViewId.data) != eventFrameTemplateView.EventFrameTemplateViewId:
					# Trying to change the name of a event frame template view to a name that already exists.
					validationError = True
			
		if validationError is True:
			raise ValidationError('The name "{}" already exists.'.format(field.data))
