from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import DateTimeField, FloatField, HiddenField, SelectField, SubmitField
from wtforms.validators import Required

class ElementAttributeValueForm(FlaskForm):
	tagId = HiddenField()
	timestamp = DateTimeField("Timestamp", default = datetime.now, validators = [Required()])
	value = FloatField("Value")
	lookupValue = SelectField("Lookup", coerce = float)
	submit = SubmitField("Save")
