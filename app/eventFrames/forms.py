from flask_wtf import FlaskForm
from datetime import datetime
from wtforms import DateTimeField, HiddenField, SelectField, StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Required, Optional
from .. models import Element

class EventFrameForm(FlaskForm):
	element = QuerySelectField("Element", validators = [Required()], get_label = "Name")
	eventFrameTemplate = QuerySelectField("Event Frame Template", validators = [Required()], get_label = "Name")
	startTimestamp = DateTimeField("Start Timestamp", default = datetime.now, validators = [Required()])
	endTimestamp = DateTimeField("End Timestamp", validators = [Optional()])
	name = StringField("Name", validators = [Optional()])
	eventFrameTemplateId = HiddenField()
	parentEventFrameId = HiddenField()
	requestReferrer = HiddenField()
	submit = SubmitField("Save")
