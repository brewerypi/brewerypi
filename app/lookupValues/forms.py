from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, StringField, SubmitField
from wtforms.validators import Length, NumberRange, Required

class LookupValueForm(FlaskForm):
	name = StringField("Name", validators = [Required(), Length(1, 45)])
	selectable = BooleanField("Selectable", validators = [NumberRange(min = 0)])
	lookupId = HiddenField()
	value = HiddenField()
	requestReferrer = HiddenField()
	submit = SubmitField("Save")
