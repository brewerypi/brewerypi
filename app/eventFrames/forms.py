from flask_wtf import FlaskForm
from datetime import datetime
from wtforms import DateTimeField, HiddenField, SubmitField
from wtforms.validators import Required, Optional

class EventFrameForm(FlaskForm):
	elementId = HiddenField()
	eventFrameTemplateId = HiddenField()
	parentEventFrameId = HiddenField()
	startTimestamp = DateTimeField("Start Timestamp", default = datetime.now, validators = [Required()])
	endTimestamp = DateTimeField("End Timestamp", validators = [Optional()])
	requestReferrer = HiddenField()
	submit = SubmitField("Save")
