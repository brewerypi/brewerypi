from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField, ValidationError
from wtforms.validators import Length, Required
from .. models import EventFrameGroup

class EventFrameGroupForm(FlaskForm):
	name = StringField("Name", validators = [Required(), Length(1, 45)])
	eventFrameGroupId = HiddenField()
	requestReferrer = HiddenField()
	submit = SubmitField("Save")

	def validate_name(self, field):
		validationError = False
		eventFrameGroup = EventFrameGroup.query.filter_by(Name = field.data).first()
		if eventFrameGroup:
			if self.eventFrameGroupId.data == "":
				# Trying to add a new event frame group using a name that already exists.
				validationError = True
			else:
				if int(self.eventFrameGroupId.data) != eventFrameGroup.EventFrameGroupId:
					# Trying to change the name of an event frame group to a name that already exists.
					validationError = True
			
		if validationError:
			raise ValidationError('The name "{}" already exists.'.format(field.data))
