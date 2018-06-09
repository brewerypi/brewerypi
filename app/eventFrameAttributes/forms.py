from datetime import datetime
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import DateTimeField, FloatField, HiddenField, SelectField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Required
from .. models import Area, ElementTemplate, Enterprise, EventFrameAttributeTemplate, EventFrame, EventFrameTemplate, Site, Tag
from .. helpers import eventFrameAttributeTemplateFullyAbbreviatedPath, eventFrameFullyAbbreviatedPath, tagFullyAbbreviatedPath

class EventFrameAttributeForm(FlaskForm):
	eventFrame = QuerySelectField("Event Frame", query_factory = lambda: EventFrame.query.join(EventFrameTemplate, ElementTemplate, Site, Enterprise)
		.order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, EventFrameTemplate.Name, EventFrame.Name), 
		get_label = eventFrameFullyAbbreviatedPath)
	eventFrameAttributeTemplate = QuerySelectField("Event Frame Attribute Template", query_factory = lambda: EventFrameAttributeTemplate.query.join(EventFrameTemplate, Site, Enterprise).order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, EventFrameTemplate.Name, EventFrameAttributeTemplate.Name), \
		get_label = eventFrameAttributeTemplateFullyAbbreviatedPath)
	tag = QuerySelectField(query_factory = lambda: Tag.query.join(Area, Site, Enterprise). \
		order_by(Enterprise.Abbreviation, Site.Abbreviation, Area.Abbreviation, Tag.Name), get_label = tagFullyAbbreviatedPath)
	submit = SubmitField("Save")

class EventFrameAttributeImportForm(FlaskForm):
	eventFrameAttributesFile = FileField("Event Frame Attributes Import File", validators = [FileRequired(), FileAllowed(["csv"], ".csv files only!")])
	submit = SubmitField("Import")

class EventFrameAttributeValueForm(FlaskForm):
	tagId = HiddenField()
	timestamp = DateTimeField("Timestamp", default = datetime.now, validators = [Required()])
	value = FloatField("Value")
	lookupValue = SelectField("Lookup", coerce = float)
	submit = SubmitField("Save")
