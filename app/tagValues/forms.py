from flask_wtf import FlaskForm
from datetime import datetime
from wtforms import DateTimeField, FloatField, HiddenField, SelectField, StringField, SubmitField
from wtforms.validators import Required
from .. models import Area, Enterprise, Lookup, Site, UnitOfMeasurement

class TagValueForm(FlaskForm):
	tagId = HiddenField()
	timestamp = DateTimeField("Timestamp", default = datetime.now, validators = [Required()])
	value = FloatField("Value")
	lookupValue = SelectField("Lookup", coerce = float)
	submit = SubmitField("Save")

class TagValueNoteForm(FlaskForm):
	note = StringField("Note", validators = [Required()])
	timestamp = DateTimeField("Timestamp", default = datetime.now, validators = [Required()])
	requestReferrer = HiddenField()
	submit = SubmitField("Save")
