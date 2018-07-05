from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, IntegerField, SubmitField
from wtforms.validators import Length, Required, ValidationError

class EventFrameAttributeTemplateForm(FlaskForm):
	name = StringField("Name", validators = [Required(), Length(1, 45)])
	description = StringField("Description", validators = [Length(0, 255)])
	submit = SubmitField("Save")

class EventFrameTemplateForm(FlaskForm):
	elementTemplateId = HiddenField()
	parentEventFrameTemplateId = HiddenField()
	name = StringField("Name", validators = [Required(), Length(1, 45)])
	order = IntegerField("Order", validators = [Required()])
	description = StringField("Description", validators = [Length(0, 255)])
	requestReferrer = HiddenField()
	submit = SubmitField("Save")
