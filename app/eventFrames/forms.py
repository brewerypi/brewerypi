from flask_wtf import FlaskForm
from datetime import datetime
from wtforms import DateTimeField, IntegerField, SelectField, StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Length, Required, Optional
from .. helpers import eventFrameFullyAbbreviatedPath, eventFrameTemplateFullyAbbreviatedPath
from .. models import ElementTemplate, Enterprise, EventFrame, EventFrameTemplate, Site

class EventFrameForm(FlaskForm):
	eventFrameTemplate = QuerySelectField("Event Frame Template", query_factory = lambda: EventFrameTemplate.query.join(ElementTemplate, Site, Enterprise). \
		order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, EventFrameTemplate.Name), get_label = eventFrameTemplateFullyAbbreviatedPath)
	name = StringField("Name", validators = [Required(), Length(1, 45)])
	description = StringField("Description", validators = [Length(0, 255)])
	parentEventFrame = QuerySelectField("Parent Event Frame", query_factory = lambda: EventFrame.query. \
		join(EventFrameTemplate, ElementTemplate, Site, Enterprise). \
		order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, EventFrameTemplate.Name, EventFrame.Name), \
		get_label = eventFrameFullyAbbreviatedPath, allow_blank = True)
	order = IntegerField("Order", validators = [Required()])
	startTime = DateTimeField("Start Time", default = datetime.now, validators = [Required()])
	endTime = DateTimeField("End Time", validators = [Optional()])
	submit = SubmitField("Save")
