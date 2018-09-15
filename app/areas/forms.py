from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField
from wtforms.validators import Length, Required

class AreaForm(FlaskForm):
	name = StringField("Name", validators = [Required(), Length(1, 45)])
	abbreviation = StringField("Abbreviation", validators = [Required(), Length(1, 10)])
	description = StringField("Description", validators = [Length(0, 255)])
	siteId = HiddenField()
	requestReferrer = HiddenField()
	submit = SubmitField("Save")
