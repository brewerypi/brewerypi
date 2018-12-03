from flask_wtf import FlaskForm
from datetime import datetime
from wtforms import DateTimeField, HiddenField, SubmitField, TextAreaField
from wtforms.validators import Required

class TagValueNoteForm(FlaskForm):
	note = TextAreaField("Note", validators = [Required()])
	timestamp = DateTimeField("Timestamp", default = datetime.utcnow, validators = [Required()])
	utcTimestamp = HiddenField()
	requestReferrer = HiddenField()
	submit = SubmitField("Save")
