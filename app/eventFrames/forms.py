from flask_wtf import FlaskForm
from datetime import datetime
from wtforms import DateTimeField, HiddenField, SelectField, StringField, SubmitField
from wtforms.validators import Required, Optional
from .. models import ElementTemplate, Enterprise, EventFrame, EventFrameTemplate, Site

class EventFrameForm(FlaskForm):
	elementId = HiddenField()
	eventFrameTemplateId = HiddenField()
	parentEventFrameId = HiddenField()
	eventFrameTemplate = SelectField("Event Frame Template", coerce = int)
	startTimestamp = DateTimeField("Start Timestamp", default = datetime.now, validators = [Required()])
	endTimestamp = DateTimeField("End Timestamp", validators = [Optional()])
	name = StringField("Name", validators = [Optional()])
	requestReferrer = HiddenField()
	submit = SubmitField("Save")
