from flask_wtf import FlaskForm
from wtforms import HiddenField, IntegerField, SelectField, StringField, SubmitField, ValidationError
from wtforms.validators import Length, Required
from .. models import EventFrameTemplate

class CopyEventFrameTemplateForm(FlaskForm):
	name = StringField("Name", validators = [Required(), Length(1, 45)])
	description = StringField("Description", validators = [Length(0, 255)])
	toElementTemplate = SelectField("To Element Template", validators = [Required()], coerce = int)
	requestReferrer = HiddenField()
	submit = SubmitField("Save")

	def validate_name(self, field):
		validationError = False
		eventFrameTemplate = EventFrameTemplate.query.filter_by(ElementTemplateId = self.toElementTemplate.data, Name = field.data).first()
		if eventFrameTemplate is not None:
			# Trying to copy an eventFrameTemplate using a name that already exists.
			validationError = True

		if validationError:
			raise ValidationError('The name "{}" already exists.'.format(field.data))

class EventFrameTemplateForm(FlaskForm):
	parentEventFrameTemplateId = HiddenField()
	name = StringField("Name", validators = [Required(), Length(1, 45)])
	order = IntegerField("Order", validators = [Required()])
	description = StringField("Description", validators = [Length(0, 255)])
	eventFrameTemplateId = HiddenField()
	elementTemplateId = HiddenField()
	parentEventFrameTemplateId = HiddenField()
	requestReferrer = HiddenField()
	submit = SubmitField("Save")

	def validate_name(self, field):
		validationError = False
		if self.elementTemplateId.data == "":
			eventFrameTemplate = EventFrameTemplate.query.filter_by(Name = field.data,
				ParentEventFrameTemplateId = self.parentEventFrameTemplateId.data).first()
		else:
			eventFrameTemplate = EventFrameTemplate.query.filter_by(ElementTemplateId = self.elementTemplateId.data, Name = field.data).first()

		if eventFrameTemplate:
			if self.eventFrameTemplateId.data == "":
				# Trying to add a new eventFrameTemplate using a name that already exists.
				validationError = True
			else:
				if int(self.eventFrameTemplateId.data) != eventFrameTemplate.EventFrameTemplateId:
					# Trying to change the name of an eventFrameTemplate to a name that already exists.
					validationError = True
			
		if validationError:
			raise ValidationError('The name "{}" already exists.'.format(field.data))

	def validate_order(self, field):
		validationError = False
		eventFrameTemplate = EventFrameTemplate.query.filter_by(Order = field.data, ParentEventFrameTemplateId = self.parentEventFrameTemplateId.data).first()
		if eventFrameTemplate:
			if self.eventFrameTemplateId.data == "":
				# Trying to add a new eventFrameTemplate using an order that already exists.
				validationError = True
			else:
				if int(self.eventFrameTemplateId.data) != eventFrameTemplate.EventFrameTemplateId:
					# Trying to change the order of an eventFrameTemplate to an order that already exists.
					validationError = True
			
		if validationError:
			raise ValidationError('The order "{}" already exists.'.format(field.data))
