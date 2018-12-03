from flask_wtf import FlaskForm
from datetime import datetime
from wtforms import DateTimeField, FloatField, HiddenField, SelectField, SubmitField
from wtforms.validators import Required

class TagValueForm(FlaskForm):
	tagId = HiddenField()
	value = FloatField("Value")
	lookupValue = SelectField("Lookup", coerce = float)
	timestamp = DateTimeField("Timestamp", default = datetime.utcnow, validators = [Required()])
	utcTimestamp = HiddenField()
	requestReferrer = HiddenField()
	submit = SubmitField("Save")
