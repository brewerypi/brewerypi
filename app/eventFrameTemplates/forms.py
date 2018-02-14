from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, IntegerField, SubmitField
from wtforms.validators import Length, Required, ValidationError
from .. models import ElementTemplate, EventFrame, EventFrameTemplate

class EventFrameTemplateForm(FlaskForm):
	elementTemplateId = HiddenField()
	parentEventFrameTemplateId = HiddenField()
	name = StringField("Name", validators = [Required(), Length(1, 45)])
	order = IntegerField("Order", validators = [Required()])
	description = StringField("Description", validators = [Length(0, 255)])
	requestReferrer = HiddenField()
	submit = SubmitField("Save")

	def validate_parentEventFrameTemplate(form, field):
		if field.data != None:
			if field.data.ElementTemplateId != form.elementTemplate.data.ElementTemplateId:
				raise ValidationError("Parent Event Frame must be blank or of the same element template type.")
