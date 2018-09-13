from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField
from wtforms.validators import Length, Required

class ElementForm(FlaskForm):
	name = StringField("Name", validators = [Required(), Length(1, 45)])
	description = StringField("Description", validators = [Length(0, 255)])
	elementIdToCopy = HiddenField()
	elementTemplateId = HiddenField()
	requestReferrer = HiddenField()
	submit = SubmitField("Save")
