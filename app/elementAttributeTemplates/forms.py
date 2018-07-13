from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField
from wtforms.validators import Length, Required

class ElementAttributeTemplateForm(FlaskForm):
	elementTemplateId = HiddenField()
	name = StringField("Name", validators = [Required(), Length(1, 45)])
	description = StringField("Description", validators = [Length(0, 255)])
	requestReferrer = HiddenField()
	submit = SubmitField("Save")
