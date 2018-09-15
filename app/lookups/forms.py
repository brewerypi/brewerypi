from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField
from wtforms.validators import Length, Required

class LookupForm(FlaskForm):
	name = StringField("Name", validators = [Required(), Length(1, 45)])
	enterpriseId = HiddenField()
	requestReferrer = HiddenField()
	submit = SubmitField("Save")
