from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Length, Required
from .. helpers import eventFrameTemplateFullyAbbreviatedPath
from .. models import ElementTemplate, EventFrameTemplate, Enterprise, Site

class EventFrameAttributeTemplateForm(FlaskForm):
	eventFrameTemplate = QuerySelectField("Event Frame Template", query_factory = lambda: EventFrameTemplate.query.join(ElementTemplate, Site, Enterprise)
		.order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, EventFrameTemplate.Name), 
		get_label = eventFrameTemplateFullyAbbreviatedPath)
	name = StringField("Name", validators = [Required(), Length(1, 45)])
	description = StringField("Description", validators = [Length(0, 255)])
	submit = SubmitField("Save")
