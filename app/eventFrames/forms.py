from flask_wtf import FlaskForm
from datetime import datetime
from wtforms import DateTimeField, HiddenField, SelectField, StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Required, Optional
from .. models import Element

class EventFrameForm(FlaskForm):
	# eventFrameTemplate = SelectField("Event Frame Template", coerce = int)
	element = QuerySelectField("Element", validators = [Required()], get_label = "Name")
	startTimestamp = DateTimeField("Start Timestamp", default = datetime.now, validators = [Required()])
	endTimestamp = DateTimeField("End Timestamp", validators = [Optional()])
	name = StringField("Name", validators = [Optional()])
	# elementId = HiddenField()
	eventFrameTemplateId = HiddenField()
	parentEventFrameId = HiddenField()
	requestReferrer = HiddenField()
	submit = SubmitField("Save")
