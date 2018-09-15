from flask_wtf import FlaskForm
from datetime import datetime
from wtforms import DateTimeField, FloatField, HiddenField, SelectField, SubmitField
from wtforms.validators import Required

class TagValueForm(FlaskForm):
	tagId = HiddenField()
	value = FloatField("Value")
	timestamp = DateTimeField("Timestamp", default = datetime.now, validators = [Required()])
	lookupValue = SelectField("Lookup", coerce = float)
	requestReferrer = HiddenField()
	submit = SubmitField("Save")
