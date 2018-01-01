from flask_wtf import FlaskForm
from datetime import datetime
from wtforms import DateTimeField, SelectField, StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Length, Required, Optional
from .. helpers import elementFullyAbbreviatedPath, eventFrameFullyAbbreviatedPath, eventFrameTemplateFullyAbbreviatedPath
from .. models import Element, ElementTemplate, Enterprise, EventFrame, EventFrameTemplate, Site

class EventFrameForm(FlaskForm):
	eventFrameTemplate = QuerySelectField("Event Frame Template", query_factory = lambda: EventFrameTemplate.query.join(ElementTemplate, Site, Enterprise).\
		order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, EventFrameTemplate.Name), get_label = eventFrameTemplateFullyAbbreviatedPath)
	element = QuerySelectField("Element", query_factory = lambda: Element.query.join(ElementTemplate, Site, Enterprise).\
		order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, Element.Name), get_label = elementFullyAbbreviatedPath)
	name = StringField("Name", validators = [Length(0, 45)])
	parentEventFrame = QuerySelectField("Parent Event Frame", query_factory = lambda: EventFrame.query. \
		join(EventFrameTemplate, ElementTemplate, Site, Enterprise). \
		order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, EventFrameTemplate.Name, EventFrame.Name), \
		get_label = eventFrameFullyAbbreviatedPath, allow_blank = True)
	startTime = DateTimeField("Start Time", default = datetime.now, validators = [Required()])
	endTime = DateTimeField("End Time", validators = [Optional()])
	description = StringField("Description", validators = [Length(0, 255)])
	submit = SubmitField("Save")
