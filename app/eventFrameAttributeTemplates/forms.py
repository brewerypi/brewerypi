from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField, ValidationError
from wtforms.validators import Length, Required
from .. models import EventFrameAttributeTemplate

class EventFrameAttributeTemplateForm(FlaskForm):
	name = StringField("Name", validators = [Required(), Length(1, 45)])
	description = StringField("Description", validators = [Length(0, 255)])
	eventFrameAttributeTemplateId = HiddenField()
	eventFrameTemplateId = HiddenField()
	requestReferrer = HiddenField()
	submit = SubmitField("Save")

	def validate_name(self, field):
		validationError = False
		eventFrameAttributeTemplate = EventFrameAttributeTemplate.query.filter_by(EventFrameTemplateId = self.eventFrameTemplateId.data,
			Name = field.data).first()
		if eventFrameAttributeTemplate:
			if self.eventFrameAttributeTemplateId.data == "":
				# Trying to add a new eventFrameAttributeTemplate using a name that already exists.
				validationError = True
			else:
				if int(self.eventFrameAttributeTemplateId.data) != eventFrameAttributeTemplate.EventFrameAttributeTemplateId:
					# Trying to change the name of an eventFrameAttributeTemplate to a name that already exists.
					validationError = True
			
		if validationError:
			raise ValidationError('The name "{}" already exists.'.format(field.data))
