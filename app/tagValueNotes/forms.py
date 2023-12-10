from flask_wtf import FlaskForm
from datetime import datetime
from wtforms import DateTimeField, HiddenField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

class TagValueNoteForm(FlaskForm):
	note = TextAreaField("Note", validators = [DataRequired()])
	timestamp = DateTimeField("Timestamp", default = datetime.utcnow, validators = [DataRequired()])
	utcTimestamp = HiddenField()
	requestReferrer = HiddenField()
	submit = SubmitField("Save")
