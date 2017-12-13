from flask_wtf import FlaskForm
from wtforms import HiddenField, IntegerField, StringField, SubmitField
from wtforms.validators import Length, Required

class LookupValueForm(FlaskForm):
	lookupId = HiddenField()
	name = StringField("Name", validators = [Required(), Length(1, 45)])
	value = IntegerField("Value", validators = [Required()])
	submit = SubmitField("Save")
