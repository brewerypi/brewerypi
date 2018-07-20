from flask_wtf import FlaskForm
from datetime import datetime
from wtforms import DateTimeField, HiddenField, StringField, SubmitField
from wtforms.validators import Required

class TagValueNoteForm(FlaskForm):
	note = StringField("Note", validators = [Required()])
	timestamp = DateTimeField("Timestamp", default = datetime.now, validators = [Required()])
	requestReferrer = HiddenField()
	submit = SubmitField("Save")
