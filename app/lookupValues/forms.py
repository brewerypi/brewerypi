from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, IntegerField, StringField, SubmitField
from wtforms.validators import Length, NumberRange, Required

class LookupValueForm(FlaskForm):
	lookupId = HiddenField()
	name = StringField("Name", validators = [Required(), Length(1, 45)])
	selectable = BooleanField("Selectable", validators = [NumberRange(min = 0)])
	value = HiddenField()
	submit = SubmitField("Save")
